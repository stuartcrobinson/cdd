#!/usr/bin/env python3
import os
import re
import time
from datetime import datetime
from pathlib import Path
import hashlib
import json
import pathspec

"""

prompt:

https://claude.ai/chat/79d661f3-b022-4315-bf71-7febab78f593
from now on when you make editing suggestions, please use the following format.  and for each item, give a brief explanation of why the given change should be made:

<<FILE>>
src/main.py
<<<SEARCH>>>
def old_function():
   x = 1
   y = 2
   return x + y
<<<REPLACE>>>
def new_function():
   result = 3
   return result
<<<END>>>

<<<FILE>>>
config/settings.json
<<<SEARCH>>>
{
   "debug": true,
   "port": 8080
}
<<<REPLACE>>>
{
   "debug": false,
   "port": 443,
   "timeout": 30
}
<<<END>>>


<<<EXPLANATION>>>

this is why the change should happen

<<<FILE>>>

src/main.py

<<<SEARCH>>>
def old_function():
   x = 1
   y = 2
   return x + y
<<<REPLACE>>>
def new_function():
   result = 3
   return result
<<<END>>>


<<<EXPLANATION>>>

this is why this change should happen

<<<FILE>>>
config/settings.json
<<<OVERWRITE>>>
{
   "debug": true,
   "port": 8080
}
<<<END>>>


"""
class FileReplacer:
    def __init__(self, input_file, max_logs=10):
        self.input_file = Path(input_file)
        self.repo_root = Path.cwd()
        self.last_hash = None
        self.processing = False
        self.max_logs = max_logs
        self.log_file = Path("scripts/replacer_history.log")
        self.gitignore_spec = self._load_gitignore()
        
    def _load_gitignore(self):
        """Load .gitignore patterns from the repository root"""
        gitignore_path = self.repo_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                return pathspec.PathSpec.from_lines('gitwildmatch', f)
        return None
    
    def _is_ignored(self, path):
        """Check if a path should be ignored according to .gitignore"""
        if not self.gitignore_spec:
            return False
        
        # Get relative path from repo root
        try:
            rel_path = path.relative_to(self.repo_root)
            return self.gitignore_spec.match_file(str(rel_path))
        except ValueError:
            # Path is outside repo root
            return False
    
    def get_file_hash(self):
        """Get hash of input file content"""
        try:
            content = self.input_file.read_text()
            return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            print(f"Cannot read input file: {e}")
            return None
    
    def parse_blocks(self, content):
        """Parse replacement blocks from content"""
        blocks = []
        
        # Remove explanation blocks first
        content = re.sub(r'<<<EXPLANATION>>>.*?(?=<<<FILE>>>|$)', '', content, flags=re.DOTALL)
        
        # Pattern for search/replace blocks
        search_pattern = r'<<<FILE>>>\s*[\r\n]+([^<]+?)[\r\n]+<<<SEARCH>>>[\r\n]+(.*?)[\r\n]+<<<REPLACE>>>[\r\n]+(.*?)[\r\n]+<<<END>>>'
        
        # Pattern for overwrite blocks
        overwrite_pattern = r'<<<FILE>>>\s*[\r\n]+([^<]+?)[\r\n]+<<<OVERWRITE>>>[\r\n]+(.*?)[\r\n]+<<<END>>>'
        
        # Find all blocks and their positions
        all_blocks = []
        
        for match in re.finditer(search_pattern, content, re.DOTALL):
            all_blocks.append((match.start(), 'search', match))
            
        for match in re.finditer(overwrite_pattern, content, re.DOTALL):
            all_blocks.append((match.start(), 'overwrite', match))
        
        # Sort by position
        all_blocks.sort(key=lambda x: x[0])
        
        block_num = 0
        for _, block_type, match in all_blocks:
            block_num += 1
            
            file_path = match.group(1).strip()
            
            # Validate block
            if not file_path:
                blocks.append({
                    'error': f"Block {block_num}: Empty file path"
                })
                continue
            
            if block_type == 'search':
                search_text = match.group(2)
                replace_text = match.group(3)
                
                if not search_text.strip():
                    blocks.append({
                        'error': f"Block {block_num}: Empty search text"
                    })
                    continue
                
                blocks.append({
                    'block_num': block_num,
                    'file': file_path,
                    'type': 'search',
                    'search': search_text,
                    'replace': replace_text
                })
            else:  # overwrite
                overwrite_text = match.group(2)
                
                blocks.append({
                    'block_num': block_num,
                    'file': file_path,
                    'type': 'overwrite',
                    'content': overwrite_text
                })
        
        return blocks
    
    def find_files(self, filename):
        """Find all matching files recursively"""
        matches = []
        
        # Handle paths with directories
        if '/' in filename:
            # Direct path from repo root
            path = self.repo_root / filename
            if path.exists() and path.is_file() and not self._is_ignored(path):
                matches.append(path)
            else:
                # Search for partial path anywhere in tree
                for path in self.repo_root.rglob('*/' + filename):
                    if path.is_file() and 'scripts/replacer_input.txt' not in str(path) and not self._is_ignored(path):
                        matches.append(path)
        else:
            # Just filename - search recursively
            for path in self.repo_root.rglob(filename):
                if path.is_file() and 'scripts/replacer_input.txt' not in str(path) and not self._is_ignored(path):
                    matches.append(path)
        
        return matches
        
    def process_replacements(self):
        """Process all replacements in input file"""
        if self.processing:
            return
        
        self.processing = True
        results = []
        
        try:
            content = self.input_file.read_text()
            
            # Log the input file contents
            self.log_input_contents(content)
            
            # Extract existing logs and clean content
            log_pattern = r'^((?:===.*?===\n.*?\n===\n\n)+)'
            log_match = re.match(log_pattern, content, re.DOTALL)
            
            existing_logs = []
            if log_match:
                existing_logs = re.findall(r'===.*?===\n.*?\n===', log_match.group(1), re.DOTALL)
                content = content[log_match.end():]
            
            blocks = self.parse_blocks(content)
            
            if not blocks:
                results.append("ERROR: No valid replacement blocks found")
            
            for block in blocks:
                if 'error' in block:
                    results.append(f"ERROR: {block['error']}")
                    continue
                
                # Validate the file path is within the repo
                try:
                    # Convert to absolute path and resolve
                    target_path = (self.repo_root / block['file']).resolve()
                    
                    # Check if the resolved path is within the repo root
                    target_path.relative_to(self.repo_root.resolve())
                except ValueError:
                    # Path is outside the repo root
                    results.append(f"ERROR Block {block['block_num']}: File path is outside repository: {block['file']}")
                    continue
                
                if block['type'] == 'overwrite':
                    # Check if the target path would be ignored
                    if self._is_ignored(target_path):
                        results.append(f"ERROR Block {block['block_num']}: File is gitignored: {target_path}")
                        continue
                    
                    try:
                        # Create parent directories if needed
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Check if file exists
                        file_exists = target_path.exists()
                        
                        # Write the content
                        target_path.write_text(block['content'])
                        action = "Overwrote" if file_exists else "Created"
                        results.append(f"SUCCESS Block {block['block_num']}: {action} {target_path}")
                        
                    except PermissionError:
                        results.append(f"ERROR Block {block['block_num']}: Permission denied: {target_path}")
                    except Exception as e:
                        results.append(f"ERROR Block {block['block_num']}: {target_path} - {str(e)}")
                else:
                    # Original search/replace logic
                    matches = self.find_files(block['file'])
                    
                    if len(matches) == 0:
                        results.append(f"ERROR Block {block['block_num']}: File not found: {block['file']}")
                    elif len(matches) > 1:
                        results.append(f"🚨🚨🚨 ERROR Block {block['block_num']}: Multiple files found for '{block['file']}' 🚨🚨🚨")
                        for m in matches:
                            results.append(f"  - {m}")
                    else:
                        target_path = matches[0]
                        try:
                            file_content = target_path.read_text()
                            
                            occurrences = file_content.count(block['search'])
                            
                            if occurrences == 0:
                                results.append(f"ERROR Block {block['block_num']}: No match found in {target_path}")
                            elif occurrences > 1:
                                results.append(f"🚨🚨🚨 ERROR Block {block['block_num']}: {occurrences} matches found in {target_path} - ABORTING 🚨🚨🚨")
                            else:
                                new_content = file_content.replace(block['search'], block['replace'], 1)
                                target_path.write_text(new_content)
                                results.append(f"SUCCESS Block {block['block_num']}: Updated {target_path}")
                                
                        except UnicodeDecodeError:
                            results.append(f"ERROR Block {block['block_num']}: Cannot read {target_path} - encoding issue")
                        except PermissionError:
                            results.append(f"ERROR Block {block['block_num']}: Permission denied: {target_path}")
                        except Exception as e:
                            results.append(f"ERROR Block {block['block_num']}: {target_path} - {str(e)}")
            
            # Prepend new log and manage log history
            if results:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_log = f"=== PROCESSED: {timestamp} ===\n" + '\n'.join(results) + "\n==="
                
                # Keep only recent logs
                all_logs = [new_log] + existing_logs[:self.max_logs-1]
                
                final_content = '\n\n'.join(all_logs) + '\n\n' + content
                self.input_file.write_text(final_content)
                
                # Print summary
                success = sum(1 for r in results if 'SUCCESS' in r)
                errors = sum(1 for r in results if 'ERROR' in r)
                print(f"Processed: {success} success, {errors} errors")
                
        except Exception as e:
            print(f"Processing error: {e}")
        finally:
            self.processing = False














    
    def log_input_contents(self, content):
        """Log the full input file contents with timestamp"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            log_entry = f"\n{'='*80}\nTIMESTAMP: {timestamp}\n{'='*80}\n{content}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    def watch(self):
        """Watch input file for changes"""
        print(f"Watching {self.input_file}...")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                current_hash = self.get_file_hash()
                
                if current_hash and current_hash != self.last_hash and not self.processing:
                    print(f"\nChange detected at {datetime.now().strftime('%H:%M:%S')}")
                    self.process_replacements()
                    self.last_hash = self.get_file_hash()
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\nStopping watcher...")
                break
            except Exception as e:
                print(f"Watch error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    replacer = FileReplacer("scripts/replacer_input.txt")
    replacer.watch()