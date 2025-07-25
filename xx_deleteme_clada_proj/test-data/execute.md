# Execute Tests

## basic operations

### 001-single-file-create

```sh sham
#!SHAM [@three-char-SHA-256: abc]
action = "file_create"
path = "/tmp/test.txt"
content = "hello world"
#!END_SHAM_abc
```

```json
{
  "success": true,
  "totalBlocks": 1,
  "executedActions": 1,
  "results": [{
    "seq": 1,
    "blockId": "abc",
    "action": "file_create",
    "params": {
      "action": "file_create",
      "path": "/tmp/test.txt",
      "content": "hello world"
    },
    "success": true
  }],
  "parseErrors": []
}
```

### 002-multiple-blocks-mixed-success

```sh sham
#!SHAM [@three-char-SHA-256: f1r]
action = "file_create"
path = "/tmp/first.txt"
content = "first"
#!END_SHAM_f1r

Some text between blocks

#!SHAM [@three-char-SHA-256: s3c]
action = "file_write"
path = "/tmp/nonexistent/second.txt"
content = "fails"
#!END_SHAM_s3c
```

```json
{
  "success": false,
  "totalBlocks": 2,
  "executedActions": 2,
  "results": [{
    "seq": 1,
    "blockId": "f1r",
    "action": "file_create",
    "params": {
      "action": "file_create",
      "path": "/tmp/first.txt",
      "content": "first"
    },
    "success": true
  }, {
    "seq": 2,
    "blockId": "s3c",
    "action": "file_write",
    "params": {
      "action": "file_write",
      "path": "/tmp/nonexistent/second.txt",
      "content": "fails"
    },
    "success": false,
    "error": "ENOENT: no such file or directory"
  }],
  "parseErrors": []
}
```

## error handling

### 003-invalid-action

```sh sham
#!SHAM [@three-char-SHA-256: inv]
action = "invalid_action"
path = "/tmp/test.txt"
#!END_SHAM_inv
```

```json
{
  "success": false,
  "totalBlocks": 1,
  "executedActions": 0,
  "results": [{
    "seq": 1,
    "blockId": "inv",
    "action": "invalid_action",
    "params": {
      "action": "invalid_action",
      "path": "/tmp/test.txt"
    },
    "success": false,
    "error": "Unknown action: invalid_action"
  }],
  "parseErrors": []
}
```

### 004-parser-error-continues

```sh sham
#!SHAM [@three-char-SHA-256: dup]
key = "first"
key = "second"
#!END_SHAM_dup

#!SHAM [@three-char-SHA-256: ok]
action = "file_create"
path = "/tmp/after-error.txt"
content = "should work"
#!END_SHAM_ok
```

```json
{
  "success": false,
  "totalBlocks": 2,
  "executedActions": 1,
  "results": [{
    "seq": 1,
    "blockId": "ok",
    "action": "file_create",
    "params": {
      "action": "file_create",
      "path": "/tmp/after-error.txt",
      "content": "should work"
    },
    "success": true
  }],
  "parseErrors": [{
    "blockId": "dup",
    "error": {
      "code": "DUPLICATE_KEY",
      "message": "Duplicate key 'key' in block 'dup'"
    }
  }]
}
```

## command execution

### 005-exec-bash

```sh sham
#!SHAM [@three-char-SHA-256: cmd]
action = "exec"
code = "echo 'hello from shell'"
lang = "bash"
#!END_SHAM_cmd
```

```json
{
  "success": true,
  "totalBlocks": 1,
  "executedActions": 1,
  "results": [{
    "seq": 1,
    "blockId": "cmd",
    "action": "exec",
    "params": {
      "action": "exec",
      "code": "echo 'hello from shell'",
      "lang": "bash"
    },
    "success": true,
    "data": {
      "stdout": "hello from shell\n",
      "stderr": "",
      "exit_code": 0
    }
  }],
  "parseErrors": []
}
```