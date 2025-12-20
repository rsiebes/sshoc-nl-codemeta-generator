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


# Add detailed summary methods to ExecutionProfiler
def _add_detailed_methods():
    """Add detailed summary methods to ExecutionProfiler class."""
    
    def get_summary_by_category(self):
        """Get execution summary grouped by category."""
        by_category = {}
        for func_name, stats in self.function_timings.items():
            if '[' in func_name and ']' in func_name:
                category = func_name.split('[')[1].split(']')[0]
            else:
                category = 'other'
            
            if category not in by_category:
                by_category[category] = []
            
            by_category[category].append((func_name, stats))
        
        return by_category
    
    def print_detailed_summary(self):
        """Print a detailed summary grouped by category."""
        if self.start_time is None:
            return
        
        total_time = time.time() - self.start_time
        
        if not self.verbose:
            return
        
        print("\n" + "=" * 100)
        print("📊 DETAILED EXECUTION SUMMARY BY CATEGORY")
        print("=" * 100)
        
        by_category = self.get_summary_by_category()
        
        # Sort categories by total time
        category_times = {}
        for category, funcs in by_category.items():
            category_times[category] = sum(f[1]['total_time'] for f in funcs)
        
        sorted_categories = sorted(category_times.items(), key=lambda x: x[1], reverse=True)
        
        for category, cat_total_time in sorted_categories:
            funcs = by_category[category]
            percent = (cat_total_time / total_time * 100) if total_time > 0 else 0
            
            print(f"\n🏷️  Category: {category.upper()}")
            print(f"   Total Time: {cat_total_time:.3f}s ({percent:.1f}%)")
            print("   " + "-" * 96)
            
            # Sort functions by time within category
            sorted_funcs = sorted(funcs, key=lambda x: x[1]['total_time'], reverse=True)
            
            for func_name, stats in sorted_funcs:
                # Clean up function name for display
                display_name = func_name.replace(f'[{category}] ', '')
                total = stats['total_time']
                count = stats['call_count']
                avg = total / count if count > 0 else 0
                cat_percent = (total / cat_total_time * 100) if cat_total_time > 0 else 0
                
                print(f"   {display_name:50} {total:8.3f}s ({cat_percent:5.1f}%) [{count:3} calls, avg {avg:.3f}s]")
            
            print("   " + "-" * 96)
        
        print("\n" + "=" * 100)
    
    def end_with_detailed_summary(self):
        """End profiler and print detailed summary."""
        if self.start_time is None:
            return
        
        total_time = time.time() - self.start_time
        
        if self.verbose:
            print("\n" + "=" * 100)
            print(f"✅ Execution completed in {total_time:.2f}s")
            print("=" * 100)
            
            if self.function_timings:
                # Print detailed summary by category
                self.print_detailed_summary()
                
                # Print overall summary
                print("\n" + "=" * 100)
                print("📈 OVERALL EXECUTION SUMMARY")
                print("=" * 100)
                
                sorted_funcs = sorted(
                    self.function_timings.items(),
                    key=lambda x: x[1]['total_time'],
                    reverse=True
                )
                
                for func_name, stats in sorted_funcs[:20]:  # Top 20
                    total = stats['total_time']
                    count = stats['call_count']
                    avg = total / count if count > 0 else 0
                    percent = (total / total_time * 100) if total_time > 0 else 0
                    
                    print(f"  {func_name:60} {total:8.3f}s ({percent:5.1f}%) [{count:3} calls, avg {avg:.3f}s]")
                
                print("=" * 100)
            print()
    
    # Add methods to ExecutionProfiler class
    ExecutionProfiler.get_summary_by_category = get_summary_by_category
    ExecutionProfiler.print_detailed_summary = print_detailed_summary
    ExecutionProfiler.end_with_detailed_summary = end_with_detailed_summary

# Add the methods when module is loaded
_add_detailed_methods()
