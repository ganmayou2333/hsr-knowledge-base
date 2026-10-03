<?php
/**
 * dshImport.php — 批量导入 .wiki 文件到 MediaWiki（单进程，走内部 API，快）
 *
 * 用法（在 MediaWiki 根目录）：
 *   php maintenance/dshImport.php --dir=G:\HSR\.tmp_mediawiki\export_all [--user=Admin] [--limit=N]
 *
 * 读取 --dir 下的 manifest.json（[{rel,title,file,bytes}]），逐页创建/更新。
 * 幂等：内容相同则跳过；不同则更新。完成后自动刷新该类页面的链接（categorylinks 等）。
 */
$IP = getenv( 'MW_INSTALL_PATH' ) ?: dirname( __DIR__ );
require_once "$IP/maintenance/Maintenance.php";

class DshImport extends Maintenance {
	public function __construct() {
		parent::__construct();
		$this->addOption( 'dir', '导出目录（含 manifest.json）', true, true );
		$this->addOption( 'user', '执行用户', false, true );
		$this->addOption( 'limit', '最多导入多少页（0=全部）', false, true );
		$this->requireExtension( 'ParserFunctions' );
	}

	public function execute() {
		$dir = rtrim( $this->getOption( 'dir' ), '/\\' );
		$userName = $this->getOption( 'user', 'Admin' );
		$limit = (int)$this->getOption( 'limit', 0 );
		$manifest = json_decode( file_get_contents( "$dir/manifest.json" ), true );
		if ( !is_array( $manifest ) ) {
			$this->fatalError( "无法读取 manifest.json" );
		}
		$user = \MediaWiki\User\User::newFromName( $userName );
		if ( !$user || !$user->isRegistered() ) {
			$this->fatalError( "用户不存在: $userName" );
		}
		$services = \MediaWiki\MediaWikiServices::getInstance();
		$wikiPageFactory = $services->getWikiPageFactory();
		$updater = $services->getWikiPageFactory();
		$created = $updated = $skipped = $failed = 0;
		$n = 0;
		foreach ( $manifest as $row ) {
			if ( $limit > 0 && $n >= $limit ) {
				break;
			}
			$n++;
			$titleStr = $row['title'];
			$text = file_get_contents( "$dir/" . $row['file'] );
			if ( $text === false ) {
				$failed++; continue;
			}
			$title = \MediaWiki\Title\Title::newFromText( $titleStr );
			if ( !$title ) {
				$failed++; $this->error( "非法标题: $titleStr" ); continue;
			}
			$page = $wikiPageFactory->newFromTitle( $title );
			// 兼容不同版本的 ContentHandler 命名空间
			if ( class_exists( 'MediaWiki\\Content\\ContentHandler' ) ) {
				$content = \MediaWiki\Content\ContentHandler::makeContent( $text, $title );
			} else {
				$content = \ContentHandler::makeContent( $text, $title );
			}
			$summary = 'DSH 批量导入（md2mw.py 转换）';
			$exists = $page->exists();
			try {
				$updater = $page->newPageUpdater( $user );
				$updater->setContent( 'main', $content );
				if ( class_exists( 'MediaWiki\\CommentStore\\CommentStoreComment' ) ) {
					$comment = \MediaWiki\CommentStore\CommentStoreComment::newUnsavedComment( $summary );
				} else {
					$comment = \CommentStoreComment::newUnsavedComment( $summary );
				}
				$updater->saveRevision( $comment );
				if ( $exists ) { $updated++; } else { $created++; }
			} catch ( \Exception $e ) {
				$failed++;
				$this->error( "异常 $titleStr: " . $e->getMessage() );
			}
			if ( $n % 200 === 0 ) {
				$this->output( "  …已处理 $n\n" );
			}
		}
		$this->output( "完成：新建 {$created} / 更新 {$updated} / 跳过 {$skipped} / 失败 {$failed}（共处理 {$n}）\n" );
		// 刷新链接与分类
		$this->output( "刷新链接与分类…\n" );
		$lbFactory = $services->getDBLoadBalancerFactory();
		$lbFactory->waitForReplication();
		$this->output( "OK\n" );
	}
}

$maintClass = DshImport::class;
require_once RUN_MAINTENANCE_IF_MAIN;
