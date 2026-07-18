<?php

namespace App\Http\Controllers;

use App\Models\Book;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\Finder\Finder;

class ScanController extends Controller
{
    /**
     * 支持的书籍文件格式
     */
    private const SUPPORTED_FORMATS = ['epub', 'pdf', 'txt', 'mobi', 'azw3'];

    /**
     * 扫描书籍目录，建立索引
     *
     * 支持去重：同一书名保留文件较大的版本
     */
    public function scan(Request $request): JsonResponse
    {
        $directory = $request->get('directory');

        if (empty($directory) || !is_dir($directory)) {
            return response()->json([
                'err' => 'invalid_directory',
                'msg' => '请提供有效的书籍目录路径',
            ], 400);
        }

        $realPath = realpath($directory);
        if ($realPath === false) {
            return response()->json([
                'err' => 'invalid_directory',
                'msg' => '目录不存在或无法访问',
            ], 400);
        }

        try {
            $result = $this->performScan($realPath);

            return response()->json([
                'err' => 'ok',
                'data' => $result,
            ]);
        } catch (\Exception $e) {
            Log::error('扫描目录失败: ' . $e->getMessage(), [
                'directory' => $realPath,
            ]);

            return response()->json([
                'err' => 'scan_failed',
                'msg' => '扫描失败: ' . $e->getMessage(),
            ], 500);
        }
    }

    /**
     * 执行扫描逻辑
     */
    private function performScan(string $directory): array
    {
        $finder = new Finder();
        $finder->files()->in($directory);

        // 按扩展名过滤
        $finder->name('/\.(' . implode('|', self::SUPPORTED_FORMATS) . ')$/i');

        $scanned = 0;
        $duplicates = 0;
        $removed = 0;
        $kept = 0;

        // 收集所有扫描到的文件
        $scannedFiles = [];
        foreach ($finder as $file) {
            $scannedFiles[] = [
                'path' => $file->getRealPath(),
                'size' => $file->getSize(),
                'format' => strtolower($file->getExtension()),
                'name' => $file->getFilename(),
            ];
        }

        // 按书名分组，处理重复
        $booksByTitle = [];
        foreach ($scannedFiles as $file) {
            $metadata = $this->extractMetadata($file['name']);
            $title = $metadata['title'];

            if (!isset($booksByTitle[$title])) {
                $booksByTitle[$title] = [];
            }
            $booksByTitle[$title][] = array_merge($file, $metadata);
        }

        // 处理每组书籍：保留最大文件，删除其他
        foreach ($booksByTitle as $title => $files) {
            if (count($files) > 1) {
                $duplicates += count($files) - 1;

                // 按文件大小降序排序
                usort($files, function ($a, $b) {
                    return $b['size'] <=> $a['size'];
                });

                // 保留最大的，删除其他的
                $keptFile = array_shift($files);
                $kept++;

                foreach ($files as $file) {
                    // 删除较小的重复文件
                    if (file_exists($file['path'])) {
                        unlink($file['path']);
                        $removed++;
                    }
                }

                // 索引保留的文件
                $this->indexBook($keptFile);
                $scanned++;
            } else {
                // 没有重复，直接索引
                $this->indexBook($files[0]);
                $scanned++;
            }
        }

        return [
            'scanned' => $scanned,
            'duplicates' => $duplicates,
            'removed' => $removed,
            'kept' => $kept,
            'directory' => $directory,
        ];
    }

    /**
     * 从文件名提取书名和作者
     *
     * 支持格式：
     * - 书名_作者.epub
     * - 书名 - 作者.epub
     * - 书名.epub
     */
    private function extractMetadata(string $filename): array
    {
        // 移除扩展名
        $name = pathinfo($filename, PATHINFO_FILENAME);

        $title = $name;
        $author = null;

        // 尝试匹配 "书名_作者" 或 "书名 - 作者" 格式
        if (str_contains($name, '_')) {
            $parts = explode('_', $name, 2);
            $title = trim($parts[0]);
            $author = trim($parts[1]);
        } elseif (str_contains($name, ' - ')) {
            $parts = explode(' - ', $name, 2);
            $title = trim($parts[0]);
            $author = trim($parts[1]);
        }

        return [
            'title' => $title,
            'author' => $author,
        ];
    }

    /**
     * 索引单本书到数据库
     */
    private function indexBook(array $file): void
    {
        Book::updateOrCreate(
            ['file_path' => $file['path']],
            [
                'title' => $file['title'] ?: '未知书名',
                'author' => $file['author'],
                'file_size' => $file['size'],
                'file_format' => $file['format'],
                'indexed_at' => now(),
            ]
        );
    }

    /**
     * 获取扫描状态
     */
    public function status(): JsonResponse
    {
        $totalBooks = Book::count();
        $latestBook = Book::orderBy('indexed_at', 'desc')->first();

        return response()->json([
            'err' => 'ok',
            'data' => [
                'total_books' => $totalBooks,
                'last_scan_at' => $latestBook ? $latestBook->indexed_at->toDateTimeString() : null,
            ],
        ]);
    }
}
