<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Setting;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // 创建管理员用户
        User::create([
            'username' => 'admin',
            'password' => Hash::make('Admin@2026'),
            'name'     => '管理员',
            'is_admin' => true,
            'active'   => true,
        ]);

        // 初始化系统设置
        $defaults = [
            'site_name'          => '搜书机器人',
            'site_description'   => '电子书搜索与下载平台',
            'download_limit'     => '10',
            'buy_link'           => '',
            'book_count_display' => '',
        ];

        foreach ($defaults as $key => $value) {
            Setting::set($key, $value);
        }
    }
}
