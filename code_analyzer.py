import os
import glob
from typing import Dict, List, Any
import git
from utils import extract_file_extension, detect_programming_language, clean_code_for_llm

class CodeAnalyzer:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.git_repo = None
        try:
            self.git_repo = git.Repo(source_dir)
        except git.InvalidGitRepositoryError:
            print("Warning: Not a git repository. Git-based analysis will be skipped.")
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze source code and return structured information."""
        result = {
            "files": self._collect_files(),
            "project_structure": self._analyze_project_structure(),
            "languages": self._detect_languages(),
            "git_info": self._extract_git_info() if self.git_repo else None,
            "key_components": self._identify_key_components()
        }
        return result
    
    def _collect_files(self) -> List[Dict[str, Any]]:
        """Collect relevant source files for analysis."""
        files = []
        for root, _, filenames in os.walk(self.source_dir):
            for filename in filenames:
                # Skip hidden files, build artifacts, etc.
                if filename.startswith('.') or any(p in root for p in ['node_modules', '__pycache__', 'build', 'dist']):
                    continue
                    
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, self.source_dir)
                ext = extract_file_extension(filename)
                
                # Skip binary files and other non-code files
                if ext not in ['py', 'js', 'ts', 'java', 'cpp', 'c', 'cs', 'go', 'rb', 'php', 'html', 'css', 'json']:
                    continue
                
                with open(file_path, 'r', errors='ignore') as f:
                    try:
                        content = f.read()
                        files.append({
                            "path": relative_path,
                            "language": detect_programming_language(ext),
                            "content": clean_code_for_llm(content),
                            "size": len(content)
                        })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return files
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project directory structure."""
        structure = {"directories": {}}
        
        for root, dirs, files in os.walk(self.source_dir):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
            
            rel_path = os.path.relpath(root, self.source_dir)
            if rel_path == '.':
                continue
                
            parts = rel_path.split(os.sep)
            current = structure["directories"]
            
            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {"directories": {}, "files": []}
                
                if i == len(parts) - 1:
                    # Add files to the deepest directory level
                    current[part]["files"] = [f for f in files if not f.startswith('.')]
                
                current = current[part]["directories"]
        
        return structure
    
    def _detect_languages(self) -> Dict[str, int]:
        """Detect programming languages used in the project."""
        languages = {}
        
        for file_info in self._collect_files():
            lang = file_info["language"]
            languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    def _extract_git_info(self) -> Dict[str, Any]:
        """Extract useful information from git repository."""
        if not self.git_repo:
            return None
            
        commits = list(self.git_repo.iter_commits(max_count=10))
        
        return {
            "active_branch": self.git_repo.active_branch.name,
            "recent_commits": [
                {
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip()
                }
                for commit in commits
            ]
        }
    
    def _identify_key_components(self) -> List[Dict[str, Any]]:
        """Identify key components in the codebase."""
        # This is a simplified implementation
        # In a real system, you'd use more sophisticated heuristics
        key_components = []
        
        # Look for patterns that might indicate important modules
        for file_info in self._collect_files():
            filename = os.path.basename(file_info["path"])
            if any(pattern in filename.lower() for pattern in ['main', 'app', 'index', 'core', 'service']):
                key_components.append({
                    "path": file_info["path"],
                    "type": "Core Component",
                    "language": file_info["language"]
                })
        
        return key_components
