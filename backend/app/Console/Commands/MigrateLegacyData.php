<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use App\Models\User;
use App\Models\Card;
use App\Models\Book;
use App\Models\Feedback;
use App\Models\SystemSetting;

class MigrateLegacyData extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'migrate:legacy {--path= : 旧数据库路径}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = '从旧版 SQLite 数据库迁移数据到 Laravel';

    /**
     * Execute the console command.
     */
    public function handle(): void
    {
        $legacyPath = $this->option('path') ?? base_path('../data/books.db');

        if (!file_exists($legacyPath)) {
            $this->error("旧数据库不存在: {$legacyPath}");
            return;
        }

        $this->info("开始从 {$legacyPath} 迁移数据...");

        // 连接旧数据库
        $legacyDb = new \PDO("sqlite:{$legacyPath}");
        $legacyDb->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);

        // 迁移用户
        $this->migrateUsers($legacyDb);

        // 迁移卡密
        $this->migrateCards($legacyDb);

        // 迁移书籍
        $this->migrateBooks($legacyDb);

        // 迁移反馈
        $this->migrateFeedbacks($legacyDb);

        // 迁移系统设置
        $this->migrateSettings($legacyDb);

        // 迁移下载记录
        $this->migrateDownloads($legacyDb);

        $this->info("数据迁移完成！");
    }

    private function migrateUsers(\PDO $legacyDb): void
    {
        $this->info("迁移用户数据...");

        $stmt = $legacyDb->query("SELECT * FROM users");
        $users = $stmt->fetchAll(\PDO::FETCH_ASSOC);

        foreach ($users as $user) {
            User::updateOrCreate(
                ['username' => $user['username']],
                [
                    'password' => $user['password_hash'], // bcrypt 哈希兼容
                    'name' => $user['name'] ?? $user['username'],
                    'email' => $user['email'] ?? null,
                    'avatar' => $user['avatar'] ?? null,
                    'is_admin' => $user['admin'] ?? false,
                    'active' => $user['active'] ?? false,
                    'expiry_date' => $user['expiry_date'] ?? null,
                    'last_login_at' => $user['last_login_at'] ?? null,
                    'created_at' => $user['created_at'] ?? now(),
                    'updated_at' => $user['updated_at'] ?? now(),
                ]
            );
        }

        $this->info("迁移了 " . count($users) . " 个用户");
    }

    private function migrateCards(\PDO $legacyDb): void
    {
        $this->info("迁移卡密数据...");

        $stmt = $legacyDb->query("SELECT * FROM cards");
        $cards = $stmt->fetchAll(\PDO::FETCH_ASSOC);

        foreach ($cards as $card) {
            Card::updateOrCreate(
                ['code' => $card['code']],
                [
                    'type' => $card['type'] ?? 'register',
                    'duration_days' => $card['duration_days'] ?? 30,
                    'used' => $card['used'] ?? false,
                    'used_by' => $card['used_by'] ?? null,
                    'used_at' => $card['used_at'] ?? null,
                    'expires_at' => $card['expires_at'] ?? null,
                    'created_at' => $card['created_at'] ?? now(),
                ]
            );
        }

        $this->info("迁移了 " . count($cards) . " 个卡密");
    }

    private function migrateBooks(\PDO $legacyDb): void
    {
        $this->info("迁移书籍数据...");

        $stmt = $legacyDb->query("SELECT * FROM books");
        $books = $stmt->fetchAll(\PDO::FETCH_ASSOC);

        foreach ($books as $book) {
            Book::updateOrCreate(
                ['file_path' => $book['file_path']],
                [
                    'title' => $book['title'] ?? '未知书名',
                    'author' => $book['author'] ?? null,
                    'file_size' => $book['file_size'] ?? 0,
                    'file_format' => $book['file_format'] ?? null,
                    'cover_path' => $book['cover_path'] ?? null,
                    'description' => $book['description'] ?? null,
                    'tags' => $book['tags'] ?? null,
                    'category' => $book['category'] ?? null,
                    'indexed_at' => $book['indexed_at'] ?? null,
                    'created_at' => $book['created_at'] ?? now(),
                ]
            );
        }

        $this->info("迁移了 " . count($books) . " 本书籍");
    }

    private function migrateFeedbacks(\PDO $legacyDb): void
    {
        $this->info("迁移反馈数据...");

        $stmt = $legacyDb->query("SELECT * FROM feedbacks");
        $feedbacks = $stmt->fetchAll(\PDO::FETCH_ASSOC);

        foreach ($feedbacks as $feedback) {
            Feedback::create([
                'user_id' => $feedback['user_id'] ?? null,
                'content' => $feedback['content'] ?? '',
                'contact' => $feedback['contact'] ?? '',
                'created_at' => $feedback['created_at'] ?? now(),
            ]);
        }

        $this->info("迁移了 " . count($feedbacks) . " 条反馈");
    }

    private function migrateSettings(\PDO $legacyDb): void
    {
        $this->info("迁移系统设置...");

        $stmt = $legacyDb->query("SELECT * FROM system_settings");
        $settings = $stmt->fetchAll(\PDO::FETCH_ASSOC);

        foreach ($settings as $setting) {
            SystemSetting::updateOrCreate(
                ['key' => $setting['key']],
                ['value' => $setting['value'] ?? '']
            );
        }

        $this->info("迁移了 " . count($settings) . " 条设置");
    }

    private function migrateDownloads(\PDO $legacyDb): void
    {
        $this->info("迁移下载记录...");

        $stmt = $legacyDb->query("SELECT * FROM user_downloads");
        $downloads = $stmt->fetchAll(\PDO::FETCH_ASSOC);

        foreach ($downloads as $download) {
            DB::table('user_downloads')->insert([
                'user_id' => $download['user_id'],
                'book_id' => $download['book_id'],
                'created_at' => $download['downloaded_at'] ?? now(),
            ]);
        }

        $this->info("迁移了 " . count($downloads) . " 条下载记录");
    }
}
