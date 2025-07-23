# MCP File Handling Guide

## The Challenge

MCP (Model Context Protocol) tools run in various environments with different filesystem constraints:
- Some environments are read-only
- Some have limited temp space
- File paths may not be directly accessible to the client

## Current Solution

The Manim Studio MCP handles this by:

1. **Fallback Directories**: If `user-data` isn't writable, it falls back to system temp directories
2. **Path Tracking**: Returns the actual file path where the video was saved
3. **Flexible Output**: Accepts any writable path in the `output_path` parameter

## Best Practices for MCP Clients

### 1. Use Absolute Paths to Writable Locations
```json
{
  "output_path": "/tmp/my_animation.mp4",
  "quality": "medium"
}
```

### 2. Check the Response
The response includes:
- `output_file`: The actual path where the file was saved
- `video_exists`: Boolean indicating if the file was created
- `video_size`: Size in bytes (if file exists)

### 3. Handle Different Environments

For cloud/containerized environments:
```json
{
  "output_path": "/workspace/output.mp4"
}
```

For local development:
```json
{
  "output_path": "./my_video.mp4"
}
```

## Alternative Approaches

### 1. Use prepare_render Instead
If you just need the Manim script without rendering:
```json
{
  "tool": "prepare_render",
  "output_path": "animation.mp4",
  "save_script": true
}
```

This returns the script path without actually rendering, avoiding filesystem issues.

### 2. Use External Storage
Future enhancement: Add support for uploading to S3, Google Cloud Storage, etc.

### 3. Streaming Output
Future enhancement: Stream video frames directly through the MCP protocol.

## Current Limitations

1. **No Direct File Transfer**: MCP doesn't support binary file transfer
2. **Path Dependencies**: Client must have access to the filesystem where files are saved
3. **Size Constraints**: Large videos may exceed protocol limits if encoded

## Recommendations

For production MCP usage:
1. Mount a shared volume between MCP server and client
2. Use cloud storage with pre-signed URLs
3. Implement a separate file service for video retrieval
4. Use lower quality settings for previews