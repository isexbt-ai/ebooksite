<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Services\R2StorageService;

class TestR2Connection extends Command
{
    protected $signature = 'r2:test';
    protected $description = '测试 Cloudflare R2 连接';

    public function handle(R2StorageService $r2)
    {
        $this->info('正在测试 R2 连接...');

        try {
            // 测试上传一个小文件
            $testContent = 'Hello, R2! Test connection.';
            $testKey = 'test/connection_' . time() . '.txt';

            $url = $r2->uploadContent($testContent, $testKey, 'text/plain');

            if ($url) {
                $this->info('R2 连接成功！');
                $this->info('测试文件 URL: ' . $url);

                // 清理测试文件
                $r2->delete($testKey);
                $this->info('测试文件已清理。');
            } else {
                $this->error('R2 连接失败：无法上传文件');
            }
        } catch (\Exception $e) {
            $this->error('R2 连接失败：' . $e->getMessage());
        }
    }
}
