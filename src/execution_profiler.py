"""
Execution Profiler

Tracks and displays execution progress and timing information for functions.
Shows which function is currently executing and how long it took.
"""

import time
import sys
from typing import Optional, Dict, List
from datetime import datetime
from functools import wraps


class ExecutionProfiler:
    """Tracks execution progress and timing of functions."""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the profiler.
        
        Args:
            verbose: Whether to print progress information
        """
        self.verbose = verbose
        self.start_time = None
        self.function_stack = []
        self.function_timings = {}
        self.indent_level = 0
    
    def start(self):
        """Start the profiler."""
        self.start_time = time.time()
        if self.verbose:
            print("\n" + "=" * 80)
            print(f"🚀 Starting execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80 + "\n")
    
    def end(self):
        """End the profiler and print summary."""
        if self.start_time is None:
            return
        
        total_time = time.time() - self.start_time
        
        if self.verbose:
            print("\n" + "=" * 80)
            print(f"✅ Execution completed in {total_time:.2f}s")
            print("=" * 80)
            
            if self.function_timings:
                print("\n📊 Function Execution Summary:")
                print("-" * 80)
                
                # Sort by total time
                sorted_funcs = sorted(
                    self.function_timings.items(),
                    key=lambda x: x[1]['total_time'],
                    reverse=True
                )
                
                for func_name, stats in sorted_funcs:
                    total = stats['total_time']
                    count = stats['call_count']
                    avg = total / count if count > 0 else 0
                    percent = (total / total_time * 100) if total_time > 0 else 0
                    
                    print(f"  {func_name:40} {total:8.3f}s ({percent:5.1f}%) [{count:3} calls, avg {avg:.3f}s]")
                
                print("-" * 80)
            print()
    
    def profile_function(self, func_name: str, category: str = ""):
        """
        Decorator to profile a function.
        
        Args:
            func_name: Name of the function
            category: Category of the function (e.g., "property", "scraper")
        
        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Format function name with category
                if category:
                    display_name = f"[{category}] {func_name}"
                else:
                    display_name = func_name
                
                # Print start message
                if self.verbose:
                    indent = "  " * self.indent_level
                    print(f"{indent}⏳ {display_name}...")
                    sys.stdout.flush()
                
                # Track function call
                self.function_stack.append(display_name)
                self.indent_level += 1
                
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start
                    
                    # Update statistics
                    if display_name not in self.function_timings:
                        self.function_timings[display_name] = {
                            'total_time': 0,
                            'call_count': 0
                        }
                    self.function_timings[display_name]['total_time'] += elapsed
                    self.function_timings[display_name]['call_count'] += 1
                    
                    # Print completion message
                    if self.verbose:
                        self.indent_level -= 1
                        indent = "  " * self.indent_level
                        print(f"{indent}✓ {display_name} ({elapsed:.3f}s)")
                        sys.stdout.flush()
                    
                    self.function_stack.pop()
                    return result
                
                except Exception as e:
                    elapsed = time.time() - start
                    
                    # Update statistics
                    if display_name not in self.function_timings:
                        self.function_timings[display_name] = {
                            'total_time': 0,
                            'call_count': 0
                        }
                    self.function_timings[display_name]['total_time'] += elapsed
                    self.function_timings[display_name]['call_count'] += 1
                    
                    # Print error message
                    if self.verbose:
                        self.indent_level -= 1
                        indent = "  " * self.indent_level
                        print(f"{indent}✗ {display_name} ({elapsed:.3f}s) - ERROR")
                        sys.stdout.flush()
                    
                    self.function_stack.pop()
                    raise
            
            return wrapper
        return decorator
    
    def log_step(self, message: str):
        """
        Log a step in execution.
        
        Args:
            message: Message to log
        """
        if self.verbose:
            indent = "  " * self.indent_level
            print(f"{indent}→ {message}")
            sys.stdout.flush()
    
    def log_info(self, message: str):
        """
        Log informational message.
        
        Args:
            message: Message to log
        """
        if self.verbose:
            indent = "  " * self.indent_level
            print(f"{indent}ℹ {message}")
            sys.stdout.flush()
    
    def log_warning(self, message: str):
        """
        Log warning message.
        
        Args:
            message: Message to log
        """
        if self.verbose:
            indent = "  " * self.indent_level
            print(f"{indent}⚠ {message}")
            sys.stdout.flush()
    
    def log_error(self, message: str):
        """
        Log error message.
        
        Args:
            message: Message to log
        """
        if self.verbose:
            indent = "  " * self.indent_level
            print(f"{indent}✗ {message}")
            sys.stdout.flush()
    
    def log_success(self, message: str):
        """
        Log success message.
        
        Args:
            message: Message to log
        """
        if self.verbose:
            indent = "  " * self.indent_level
            print(f"{indent}✓ {message}")
            sys.stdout.flush()


# Global profiler instance
_profiler = None


def get_profiler(verbose: bool = True) -> ExecutionProfiler:
    """
    Get or create the global profiler instance.
    
    Args:
        verbose: Whether to print progress information
    
    Returns:
        ExecutionProfiler instance
    """
    global _profiler
    if _profiler is None:
        _profiler = ExecutionProfiler(verbose=verbose)
    return _profiler


def profile(func_name: str = "", category: str = ""):
    """
    Decorator to profile a function using the global profiler.
    
    Args:
        func_name: Name of the function (auto-detected if empty)
        category: Category of the function
    
    Returns:
        Decorator function
    """
    def decorator(func):
        name = func_name or func.__name__
        profiler = get_profiler()
        return profiler.profile_function(name, category)(func)
    return decorator
