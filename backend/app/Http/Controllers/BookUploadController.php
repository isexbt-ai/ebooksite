<?php

namespace App\Http\Controllers;

use App\Models\Book;
use App\Services\R2StorageService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;

class BookUploadController extends Controller
{
    protected R2StorageService $r2;
    protected int $chunkSize;

    public function __construct(R2StorageService $r2)
    {
        $this->r2 = $r2;
        $this->chunkSize = 5 * 1024 * 1024; // 5MB 分片
    }

    public function initiateMultipart(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'title'    => 'required|string|max:255',
            'author'   => 'required|string|max:255',
            'category' => 'nullable|string|max:50',
            'file_name'=> 'required|string',
            'file_size'=> 'required|integer',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $extension = pathinfo($request->file_name, PATHINFO_EXTENSION);
        $key = sprintf(
            'novels/%s/%s_%s.%s',
            date('Y/m'),
            Str::slug($request->title),
            uniqid(),
            $extension
        );

        $uploadId = $this->r2->initiateMultipartUpload($key);

        if (!$uploadId) {
            return response()->json(['message' => '初始化分片上传失败'], 500);
        }

        $totalChunks = ceil($request->file_size / $this->chunkSize);

        $book = Book::create([
            'title'         => $request->title,
            'author'        => $request->author,
            'category'      => $request->category,
            'r2_key'        => $key,
            'file_size'     => $request->file_size,
            'mime_type'     => $request->input('mime_type', 'application/octet-stream'),
            'upload_status' => 'uploading',
            'upload_id'     => $uploadId,
            'uploader_id'   => auth()->id(),
        ]);

        return response()->json([
            'message'      => '初始化成功',
            'book_id'      => $book->id,
            'upload_id'    => $uploadId,
            'key'          => $key,
            'chunk_size'   => $this->chunkSize,
            'total_chunks' => $totalChunks,
        ]);
    }

    public function uploadChunk(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'book_id'     => 'required|integer',
            'upload_id'   => 'required|string',
            'part_number' => 'required|integer|min:1',
            'chunk'       => 'required|file',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $book = Book::findOrFail($request->book_id);

        if ($book->upload_id !== $request->upload_id) {
            return response()->json(['message' => '上传ID不匹配'], 400);
        }

        $chunk = $request->file('chunk');
        $content = file_get_contents($chunk->getRealPath());
        $contentMd5 = base64_encode(md5($content, true));

        $part = $this->r2->uploadPart(
            $book->r2_key,
            $request->upload_id,
            $request->part_number,
            $content,
            $contentMd5
        );

        if (!$part) {
            return response()->json(['message' => '分片上传失败'], 500);
        }

        $parts = $book->upload_parts ? json_decode($book->upload_parts, true) : [];
        $parts[] = $part;
        $book->upload_parts = json_encode($parts);
        $book->save();

        return response()->json([
            'message'      => '分片上传成功',
            'part_number'  => $request->part_number,
            'etag'         => $part['ETag'],
        ]);
    }

    public function completeMultipart(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'book_id'   => 'required|integer',
            'upload_id' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $book = Book::findOrFail($request->book_id);

        if ($book->upload_id !== $request->upload_id) {
            return response()->json(['message' => '上传ID不匹配'], 400);
        }

        $parts = json_decode($book->upload_parts, true);

        if (empty($parts)) {
            return response()->json(['message' => '没有分片数据'], 400);
        }

        $url = $this->r2->completeMultipartUpload($book->r2_key, $request->upload_id, $parts);

        if (!$url) {
            return response()->json(['message' => '完成上传失败'], 500);
        }

        $book->r2_url = $url;
        $book->upload_status = 'completed';
        $book->save();

        return response()->json([
            'message' => '上传完成',
            'book'    => $book,
        ]);
    }

    public function abortMultipart(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'book_id'   => 'required|integer',
            'upload_id' => 'required|string',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $book = Book::findOrFail($request->book_id);

        if ($book->upload_id !== $request->upload_id) {
            return response()->json(['message' => '上传ID不匹配'], 400);
        }

        $this->r2->abortMultipartUpload($book->r2_key, $request->upload_id);
        $book->delete();

        return response()->json(['message' => '上传已取消']);
    }

    public function upload(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'title'    => 'required|string|max:255',
            'author'   => 'required|string|max:255',
            'file'     => 'required|file|mimes:txt,epub,pdf,mobi,azw3|max:52428800',
            'category' => 'nullable|string|max:50',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $file = $request->file('file');
        $extension = $file->getClientOriginalExtension();

        $key = sprintf(
            'novels/%s/%s_%s.%s',
            date('Y/m'),
            Str::slug($request->title),
            uniqid(),
            $extension
        );

        $url = $this->r2->upload($file->getRealPath(), $key, $file->getMimeType());

        if (!$url) {
            return response()->json(['message' => '上传失败'], 500);
        }

        $book = Book::create([
            'title'         => $request->title,
            'author'        => $request->author,
            'category'      => $request->category,
            'r2_key'        => $key,
            'r2_url'        => $url,
            'file_size'     => $file->getSize(),
            'mime_type'     => $file->getMimeType(),
            'upload_status' => 'completed',
            'uploader_id'   => auth()->id(),
        ]);

        return response()->json([
            'message' => '上传成功',
            'book'    => $book,
        ]);
    }

    public function download(int $id)
    {
        $book = Book::findOrFail($id);

        if ($book->upload_status !== 'completed') {
            return response()->json(['message' => '文件尚未上传完成'], 400);
        }

        $url = $this->r2->getPresignedUrl($book->r2_key);

        if (!$url) {
            return response()->json(['message' => '生成下载链接失败'], 500);
        }

        return response()->json([
            'download_url' => $url,
            'expires_at'   => now()->addSeconds(config('services.r2.presigned_expires', 3600)),
        ]);
    }

    public function destroy(int $id)
    {
        $book = Book::findOrFail($id);

        if ($book->r2_key) {
            $this->r2->delete($book->r2_key);
        }

        $book->delete();

        return response()->json(['message' => '删除成功']);
    }

    public function batchUpload(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'books' => 'required|array',
            'books.*.title'  => 'required|string|max:255',
            'books.*.author' => 'required|string|max:255',
            'books.*.file'   => 'required|file|mimes:txt,epub,pdf,mobi,azw3|max:52428800',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

        $results = [];
        $errors = [];

        foreach ($request->books as $index => $bookData) {
            try {
                $file = $bookData['file'];
                $extension = $file->getClientOriginalExtension();

                $key = sprintf(
                    'novels/%s/%s_%s.%s',
                    date('Y/m'),
                    Str::slug($bookData['title']),
                    uniqid(),
                    $extension
                );

                $url = $this->r2->upload($file->getRealPath(), $key, $file->getMimeType());

                if (!$url) {
                    $errors[] = ['index' => $index, 'message' => '上传失败'];
                    continue;
                }

                $book = Book::create([
                    'title'         => $bookData['title'],
                    'author'        => $bookData['author'],
                    'category'      => $bookData['category'] ?? null,
                    'r2_key'        => $key,
                    'r2_url'        => $url,
                    'file_size'     => $file->getSize(),
                    'mime_type'     => $file->getMimeType(),
                    'upload_status' => 'completed',
                    'uploader_id'   => auth()->id(),
                ]);

                $results[] = $book;
            } catch (\Exception $e) {
                $errors[] = ['index' => $index, 'message' => $e->getMessage()];
            }
        }

        return response()->json([
            'message' => '批量上传完成',
            'success' => count($results),
            'failed'  => count($errors),
            'books'   => $results,
            'errors'  => $errors,
        ]);
    }


    public function batchUploadWithDedup(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'files' => 'required|array',
            'files.*' => 'required|file|mimes:txt,epub,pdf,mobi,azw3|max:52428800',
        ]);

        if ($validator->fails()) {
            return response()->json(['errors' => $validator->errors()], 422);
        }

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

        return response()->json([
            'err'        => 'ok',
            'message'    => '批量上传完成',
            'success'    => count($results),
            'duplicates' => count($duplicates),
            'failed'     => count($errors),
            'books'      => $results,
            'dup_list'   => $duplicates,
            'errors'     => $errors,
        ]);
    }
}
