<?php

namespace App\Http\Controllers;

use App\Models\Book;
use App\Models\AuditLog;
use App\Services\R2StorageService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Str;

class BookUploadController extends Controller
{
    protected R2StorageService $r2;
    protected int $chunkSize;

    public function __construct(R2StorageService $r2)
    {
        parent::__construct();
        $this->r2 = $r2;
        $this->chunkSize = 5 * 1024 * 1024; // 5MB 分片
    }

    /**
     * 单文件上传
     */
    public function upload(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'title'    => 'nullable|string|max:255',
            'author'   => 'nullable|string|max:255',
            'file'     => 'required|file|mimes:txt,epub,pdf,mobi,azw3|max:52428800',
            'category' => 'nullable|string|max:50',
            'tags'     => 'nullable|string|max:255',
            'description' => 'nullable|string|max:2000',
        ]);

        $file = $request->file('file');
        $extension = $file->getClientOriginalExtension();
        $fileHash = hash_file('md5', $file->getRealPath());

        // 自动从文件名提取书名和作者
        $title = $validated['title'] ?? pathinfo($file->getClientOriginalName(), PATHINFO_FILENAME);
        $author = $validated['author'] ?? '未知';

        $key = sprintf(
            'novels/%s/%s_%s.%s',
            date('Y/m'),
            Str::slug($title),
            uniqid(),
            $extension
        );

        $url = $this->r2->upload($file->getRealPath(), $key, $file->getMimeType());

        if (!$url) {
            return $this->api->error('上传失败', 3001, 500);
        }

        $book = Book::create([
            'title'         => $title,
            'author'        => $author,
            'category'      => $validated['category'] ?? null,
            'tags'          => $validated['tags'] ?? null,
            'description'   => $validated['description'] ?? null,
            'r2_key'        => $key,
            'r2_url'        => $url,
            'file_size'     => $file->getSize(),
            'file_format'   => $extension,
            'mime_type'     => $file->getMimeType(),
            'upload_status' => 'completed',
            'uploader_id'   => auth()->id(),
            'file_hash'     => $fileHash,
        ]);

        AuditLog::log('upload', 'book', $book->id);

        return $this->api->success($book, '上传成功', 201);
    }

    /**
     * 初始化分片上传
     */
    public function initiateMultipart(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'title'     => 'required|string|max:255',
            'author'    => 'required|string|max:255',
            'category'  => 'nullable|string|max:50',
            'file_name' => 'required|string',
            'file_size' => 'required|integer',
            'mime_type' => 'nullable|string',
        ]);

        $extension = pathinfo($validated['file_name'], PATHINFO_EXTENSION);
        $key = sprintf(
            'novels/%s/%s_%s.%s',
            date('Y/m'),
            Str::slug($validated['title']),
            uniqid(),
            $extension
        );

        $uploadId = $this->r2->initiateMultipartUpload($key, $validated['mime_type'] ?? null);

        if (!$uploadId) {
            return $this->api->error('初始化分片上传失败', 3002, 500);
        }

        $totalChunks = ceil($validated['file_size'] / $this->chunkSize);

        $book = Book::create([
            'title'         => $validated['title'],
            'author'        => $validated['author'],
            'category'      => $validated['category'] ?? null,
            'r2_key'        => $key,
            'file_size'     => $validated['file_size'],
            'file_format'   => $extension,
            'mime_type'     => $validated['mime_type'] ?? 'application/octet-stream',
            'upload_status' => 'uploading',
            'upload_id'     => $uploadId,
            'uploader_id'   => auth()->id(),
        ]);

        return $this->api->success([
            'book_id'      => $book->id,
            'upload_id'    => $uploadId,
            'key'          => $key,
            'chunk_size'   => $this->chunkSize,
            'total_chunks' => $totalChunks,
        ], '初始化成功');
    }

    /**
     * 上传分片
     */
    public function uploadChunk(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'book_id'     => 'required|integer',
            'upload_id'   => 'required|string',
            'part_number' => 'required|integer|min:1',
            'chunk'       => 'required|file',
        ]);

        $book = Book::findOrFail($validated['book_id']);

        if ($book->upload_id !== $validated['upload_id']) {
            return $this->api->error('上传ID不匹配', 3003);
        }

        $chunk = $request->file('chunk');
        $content = file_get_contents($chunk->getRealPath());
        $contentMd5 = base64_encode(md5($content, true));

        $part = $this->r2->uploadPart(
            $book->r2_key,
            $validated['upload_id'],
            $validated['part_number'],
            $content,
            $contentMd5
        );

        if (!$part) {
            return $this->api->error('分片上传失败', 3004, 500);
        }

        $parts = $book->upload_parts ?? [];
        $parts[] = $part;
        $book->upload_parts = $parts;
        $book->save();

        return $this->api->success([
            'part_number' => $validated['part_number'],
            'etag'        => $part['ETag'],
        ], '分片上传成功');
    }

    /**
     * 完成分片上传
     */
    public function completeMultipart(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'book_id'   => 'required|integer',
            'upload_id' => 'required|string',
        ]);

        $book = Book::findOrFail($validated['book_id']);

        if ($book->upload_id !== $validated['upload_id']) {
            return $this->api->error('上传ID不匹配', 3003);
        }

        $parts = $book->upload_parts;

        if (empty($parts)) {
            return $this->api->error('没有分片数据', 3005);
        }

        $url = $this->r2->completeMultipartUpload($book->r2_key, $validated['upload_id'], $parts);

        if (!$url) {
            return $this->api->error('完成上传失败', 3006, 500);
        }

        $book->update([
            'r2_url'        => $url,
            'upload_status' => 'completed',
        ]);

        AuditLog::log('upload_multipart', 'book', $book->id);

        return $this->api->success($book, '上传完成');
    }

    /**
     * 取消分片上传
     */
    public function abortMultipart(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'book_id'   => 'required|integer',
            'upload_id' => 'required|string',
        ]);

        $book = Book::findOrFail($validated['book_id']);

        if ($book->upload_id !== $validated['upload_id']) {
            return $this->api->error('上传ID不匹配', 3003);
        }

        $this->r2->abortMultipartUpload($book->r2_key, $validated['upload_id']);
        $book->delete();

        return $this->api->success(null, '上传已取消');
    }

    /**
     * 批量上传（带去重）
     */
    public function batchUploadDedup(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'files'          => 'required|array',
            'files.*'        => 'required|file|mimes:txt,epub,pdf,mobi,azw3|max:52428800',
            'titles'         => 'nullable|array',
            'authors'        => 'nullable|array',
        ]);

        $results = [];
        $duplicates = [];
        $errors = [];

        foreach ($request->file('files') as $index => $file) {
            try {
                $fileHash = hash_file('md5', $file->getRealPath());
                $fileSize = $file->getSize();

                $existingBook = Book::where('file_hash', $fileHash)->first();

                if ($existingBook) {
                    if ($fileSize > $existingBook->file_size) {
                        $this->r2->delete($existingBook->r2_key);

                        $extension = $file->getClientOriginalExtension();
                        $key = sprintf(
                            'novels/%s/%s_%s.%s',
                            date('Y/m'),
                            Str::slug($existingBook->title),
                            uniqid(),
                            $extension
                        );

                        $url = $this->r2->upload($file->getRealPath(), $key, $file->getMimeType());

                        if ($url) {
                            $existingBook->update([
                                'r2_key'    => $key,
                                'r2_url'    => $url,
                                'file_size' => $fileSize,
                                'file_hash' => $fileHash,
                            ]);
                            $duplicates[] = [
                                'index' => $index,
                                'title' => $existingBook->title,
                                'action' => 'replaced',
                            ];
                        }
                    } else {
                        $duplicates[] = [
                            'index' => $index,
                            'title' => $existingBook->title,
                            'action' => 'skipped',
                        ];
                    }
                    continue;
                }

                $extension = $file->getClientOriginalExtension();
                $title = $request->input("titles.$index", $file->getClientOriginalName());
                $author = $request->input("authors.$index", 'Unknown');

                $key = sprintf(
                    'novels/%s/%s_%s.%s',
                    date('Y/m'),
                    Str::slug($title),
                    uniqid(),
                    $extension
                );

                $url = $this->r2->upload($file->getRealPath(), $key, $file->getMimeType());

                if (!$url) {
                    $errors[] = ['index' => $index, 'message' => 'R2上传失败'];
                    continue;
                }

                $book = Book::create([
                    'title'         => $title,
                    'author'        => $author,
                    'r2_key'        => $key,
                    'r2_url'        => $url,
                    'file_size'     => $fileSize,
                    'file_format'   => $extension,
                    'file_hash'     => $fileHash,
                    'mime_type'     => $file->getMimeType(),
                    'upload_status' => 'completed',
                    'uploader_id'   => auth()->id(),
                ]);

                $results[] = $book;
            } catch (\Exception $e) {
                $errors[] = ['index' => $index, 'message' => $e->getMessage()];
            }
        }

        AuditLog::log('batch_upload', 'book', null, null, [
            'success'    => count($results),
            'duplicates' => count($duplicates),
            'failed'     => count($errors),
        ]);

        return $this->api->success([
            'success'    => count($results),
            'duplicates' => count($duplicates),
            'failed'     => count($errors),
            'books'      => $results,
            'dup_list'   => $duplicates,
            'errors'     => $errors,
        ], '批量上传完成');
    }

    /**
     * 删除书籍
     */
    public function destroy(int $id): JsonResponse
    {
        $book = Book::find($id);

        if (!$book) {
            return $this->api->notFound('书籍不存在');
        }

        if ($book->r2_key) {
            $this->r2->delete($book->r2_key);
        }

        $book->delete();

        AuditLog::log('delete', 'book', $id);

        return $this->api->success(null, '删除成功');
    }
}
