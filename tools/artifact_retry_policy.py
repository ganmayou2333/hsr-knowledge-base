"""纯逻辑的 PR 预览产物下载重试策略。

本模块不访问网络、不读取仓库内容：调用方传入「尝试序号」「上一次失败文本」
和「本调用之前已经等待的秒数」，模块返回失败分类、是否还允许重试、还需等待
多少秒以及可读的原因说明。

约定：

* 尝试序号从 1 开始，最多 ``MAX_ATTEMPTS`` 次（默认 3 次）。
* 两次尝试之间依次等待 ``BACKOFF_SECONDS``（5 秒、10 秒）。
* ``failure_text`` 为 ``None``、空字符串或成功标记时表示该次下载成功。
* 失败分为可重试（暂时性）与不可重试两类；只有可重试且未超过次数时才会
  返回 ``retry=True``。不可重试的错误直接失败，不做无意义重试。
* ``waited_seconds`` 用于避免重复等待：实际等待时间 = max(0, 退避秒数 - 已等待秒数)。

命令行接口供工作流调用，例如::

    python -X utf8 tools/artifact_retry_policy.py --attempt 1 \
        --failure-file "$RUNNER_TEMP/preview-attempt-1-failure.txt" \
        --github-output "$GITHUB_OUTPUT" --summary-file "$RUNNER_TEMP/attempts.md"

退出码：0 表示成功或允许重试；1 表示策略判定失败（不可重试或次数用尽），
工作流据此让该步骤失败，从而不会被 ``continue-on-error`` 误读为成功。
``--diagnose-only`` 只用于「下载步骤本身已经让任务失败」的最终尝试，用来补
充诊断信息而不再改变任务结论。
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (5, 10)

CATEGORY_SUCCESS = "success"
CATEGORY_NAME_NOT_FOUND = "name-not-found"
CATEGORY_ID_NOT_FOUND = "id-not-found"
CATEGORY_PERMISSION_OR_404 = "permission-or-404"
CATEGORY_DIGEST_MISMATCH = "digest-mismatch"
CATEGORY_UNKNOWN = "unknown"

#: 分类 → 该分类是否属于「非暂时性、不应继续重试」。
NON_RETRYABLE_CATEGORIES = frozenset(
    {
        CATEGORY_PERMISSION_OR_404,
        CATEGORY_DIGEST_MISMATCH,
    }
)

# 顺序有意义：先匹配更具体的错误，再匹配通用的「not found / 404」。
DIGEST_MISMATCH_PATTERNS = (
    "digest mismatch",
    "digest-mismatch",
    "digest did not match",
    "digest validation failed",
    "digest verification failed",
    "checksum mismatch",
    "sha-256 mismatch",
    "sha256 mismatch",
    "integrity check failed",
)
NAME_NOT_FOUND_PATTERNS = (
    "unable to find any artifacts for the associated workflow",
    "no artifacts have been found for this workflow run",
    "unable to find any artifacts",
    "artifact not found for name",
    "no artifact named",
    "artifact not found by name",
)
ID_NOT_FOUND_PATTERNS = (
    "no artifacts found",
    "no artifact was found",
    "no artifact with id",
    "artifact id not found",
)
PERMISSION_PATTERNS = (
    "resource not accessible",
    "permission denied",
    "insufficient permission",
    "not authorized",
    "unauthorized",
    "forbidden",
    "access denied",
    "http 401",
    "http 403",
    " 401 ",
    " 403 ",
)
HTTP_404_PATTERNS = (
    "http 404",
    "404 not found",
    "not found",
)

_SUCCESS_MARKERS = frozenset({"", "success", "succeeded", "ok", "no failure"})


@dataclass(frozen=True)
class RetryDecision:
    """一次失败（或成功）之后的重试判定结果。"""

    attempt: int
    category: str
    retry: bool
    wait_seconds: int
    reason: str
    attempts_remaining: int

    @property
    def action(self) -> str:
        """返回 ``success`` / ``retry`` / ``fail`` 三态结论。"""
        if self.category == CATEGORY_SUCCESS:
            return "success"
        return "retry" if self.retry else "fail"


def _normalize(failure_text: str | None) -> str:
    if failure_text is None:
        return ""
    return " ".join(str(failure_text).lower().split())


def _matches(normalized: str, patterns: Iterable[str]) -> bool:
    return any(pattern in normalized for pattern in patterns)


def classify_failure(failure_text: str | None) -> str:
    """把失败文本归类为模块中定义的分类；空文本视为成功。

    该函数只看文本，不访问网络、不读取文件，便于单元测试。
    """
    normalized = _normalize(failure_text)
    if normalized in _SUCCESS_MARKERS:
        return CATEGORY_SUCCESS
    if _matches(normalized, DIGEST_MISMATCH_PATTERNS):
        return CATEGORY_DIGEST_MISMATCH
    if _matches(normalized, NAME_NOT_FOUND_PATTERNS):
        return CATEGORY_NAME_NOT_FOUND
    if _matches(normalized, ID_NOT_FOUND_PATTERNS):
        return CATEGORY_ID_NOT_FOUND
    if _matches(normalized, PERMISSION_PATTERNS):
        return CATEGORY_PERMISSION_OR_404
    if _matches(normalized, HTTP_404_PATTERNS):
        return CATEGORY_PERMISSION_OR_404
    return CATEGORY_UNKNOWN


def category_description(category: str) -> str:
    """返回分类的可读解释，用于日志与摘要。"""
    return {
        CATEGORY_SUCCESS: "download succeeded",
        CATEGORY_NAME_NOT_FOUND: "artifact not visible by name yet (known transient visibility lag)",
        CATEGORY_ID_NOT_FOUND: "artifact listed but not retrievable yet (known transient)",
        CATEGORY_PERMISSION_OR_404: "access denied or artifact/run definitively absent; retrying cannot fix this",
        CATEGORY_DIGEST_MISMATCH: "downloaded bytes do not match the recorded digest; retrying cannot fix corruption or tampering",
        CATEGORY_UNKNOWN: "failure is not recognisably transient, so retries are strictly bounded",
    }.get(category, "unclassified failure")


def _validate_attempt(attempt: int) -> None:
    if not isinstance(attempt, int) or isinstance(attempt, bool):
        raise TypeError("attempt must be an integer")
    if attempt < 1:
        raise ValueError("attempt must be >= 1")


def decide(attempt: int, failure_text: str | None = None, waited_seconds: int = 0) -> RetryDecision:
    """根据一次尝试的结果决定是否重试、还需等待多久。

    参数
    ----
    attempt:
        刚结束的这一次尝试的序号（从 1 开始）。超过 ``MAX_ATTEMPTS`` 时按
        「次数用尽」处理，返回失败。
    failure_text:
        该次尝试的失败文本；``None``/空字符串/``success`` 表示成功。
    waited_seconds:
        本次调用之前，调用方为这一次失败已经等待过的秒数（>= 0）。
    """
    _validate_attempt(attempt)
    if not isinstance(waited_seconds, int) or isinstance(waited_seconds, bool):
        raise TypeError("waited_seconds must be an integer")
    if waited_seconds < 0:
        raise ValueError("waited_seconds must be >= 0")
    if not isinstance(failure_text, (str, type(None))):
        raise TypeError("failure_text must be a string or None")

    category = classify_failure(failure_text)
    remaining = max(0, MAX_ATTEMPTS - attempt)

    if category == CATEGORY_SUCCESS:
        return RetryDecision(
            attempt=attempt,
            category=category,
            retry=False,
            wait_seconds=0,
            reason=f"Attempt {attempt}/{MAX_ATTEMPTS} download succeeded; no retry needed.",
            attempts_remaining=remaining,
        )

    if category in NON_RETRYABLE_CATEGORIES:
        return RetryDecision(
            attempt=attempt,
            category=category,
            retry=False,
            wait_seconds=0,
            reason=(
                f"Attempt {attempt}/{MAX_ATTEMPTS} failed with non-retryable category "
                f"{category} ({category_description(category)}); not retrying."
            ),
            attempts_remaining=remaining,
        )

    if attempt >= MAX_ATTEMPTS:
        return RetryDecision(
            attempt=attempt,
            category=category,
            retry=False,
            wait_seconds=0,
            reason=(
                f"Attempt {attempt}/{MAX_ATTEMPTS} failed ({category}) and the "
                f"{MAX_ATTEMPTS}-attempt budget is exhausted; final failure."
            ),
            attempts_remaining=0,
        )

    backoff = BACKOFF_SECONDS[attempt - 1]
    wait_seconds = max(0, backoff - waited_seconds)
    return RetryDecision(
        attempt=attempt,
        category=category,
        retry=True,
        wait_seconds=wait_seconds,
        reason=(
            f"Attempt {attempt}/{MAX_ATTEMPTS} failed as {category} "
            f"({category_description(category)}); waiting {wait_seconds}s before attempt "
            f"{attempt + 1} (backoff {backoff}s, already waited {waited_seconds}s)."
        ),
        attempts_remaining=remaining,
    )


def _single_line(value: str) -> str:
    return " ".join(str(value).split())


def _append_kv(path: str, decision: RetryDecision) -> None:
    lines = [
        f"retry={'true' if decision.retry else 'false'}",
        f"wait_seconds={decision.wait_seconds}",
        f"category={decision.category}",
        f"reason={_single_line(decision.reason)}",
    ]
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def _append_summary(path: str, decision: RetryDecision) -> None:
    if decision.category == CATEGORY_SUCCESS:
        bullet = f"- Attempt {decision.attempt}: success; no retry needed."
    elif decision.retry:
        bullet = (
            f"- Attempt {decision.attempt}: failed ({decision.category}); "
            f"waiting {decision.wait_seconds}s before attempt {decision.attempt + 1}."
        )
    else:
        bullet = (
            f"- Attempt {decision.attempt}: failed ({decision.category}); "
            "no further retry (see the policy reason in the step log)."
        )
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(bullet + "\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Decide whether a failed preview artifact download should be retried (pure policy, no network).",
    )
    parser.add_argument("--attempt", type=int, required=True, help="1-based number of the attempt that just finished.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--failure-text", default=None, help="Failure text of that attempt; omit for success.")
    source.add_argument("--failure-file", default=None, help="Read the failure text from this file instead.")
    parser.add_argument("--waited-seconds", type=int, default=0, help="Seconds already spent waiting since that attempt.")
    parser.add_argument("--github-output", default=None, help="Append retry/wait_seconds/category/reason key-value pairs to this file.")
    parser.add_argument("--summary-file", default=None, help="Append a markdown bullet describing the decision to this file.")
    parser.add_argument(
        "--diagnose-only",
        action="store_true",
        help="Always exit 0 after writing diagnostics; use only when the job already failed at the download step.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        failure_text: str | None = args.failure_text
        if args.failure_file is not None:
            failure_text = Path(args.failure_file).read_text(encoding="utf-8", errors="replace")
        decision = decide(args.attempt, failure_text, args.waited_seconds)
        if args.github_output:
            _append_kv(args.github_output, decision)
        if args.summary_file:
            _append_summary(args.summary_file, decision)
    except (OSError, TypeError, ValueError) as exc:
        message = f"Preview download retry policy could not evaluate attempt {args.attempt}: {exc}"
        print(f"::error::{message}")
        return 2

    if decision.category == CATEGORY_SUCCESS:
        print(decision.reason)
    elif decision.retry:
        print(f"::warning::{decision.reason}")
    else:
        print(f"::error::{decision.reason}")

    if decision.action == "fail" and not args.diagnose_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
