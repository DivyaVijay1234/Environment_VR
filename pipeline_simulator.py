"""
Pipeline Stage Simulator
Demonstrates the advantage of pipelining (parallel stages) over sequential execution.
Shows how sharing stages between flood and fire paths reduces total time.
"""

import time
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Task:
    name: str
    duration: float  # seconds

@dataclass
class StageResult:
    stage: str
    task: str
    start_time: float
    end_time: float
    duration: float

class PipelineSimulator:
    """Simulates a multi-stage pipeline with configurable workers per stage."""
    
    def __init__(self):
        self.results: List[StageResult] = []
        self.stage_occupancy: Dict[str, List[tuple]] = defaultdict(list)
        
    def run_sequential(self, tasks: List[Task], stages: List[str]) -> float:
        """
        Run tasks sequentially through all stages.
        Each task must complete ALL stages before next task starts.
        """
        print("\n=== SEQUENTIAL EXECUTION ===")
        current_time = 0.0
        
        for task in tasks:
            for stage in stages:
                # Find stage duration (simulated)
                stage_duration = task.duration * 0.3  # Each stage takes 30% of task time
                start = current_time
                end = start + stage_duration
                
                self.results.append(StageResult(
                    stage=stage,
                    task=task.name,
                    start_time=start,
                    end_time=end,
                    duration=stage_duration
                ))
                current_time = end
                print(f"  {task.name:20} → {stage:20} [{start:6.2f}s - {end:6.2f}s]")
        
        return current_time
    
    def run_pipelined(self, tasks: List[Task], stages: List[str], workers_per_stage: int = 1) -> float:
        """
        Run tasks through stages in a pipelined manner.
        Stages can process different tasks in parallel (pipeline effect).
        """
        print(f"\n=== PIPELINED EXECUTION ({workers_per_stage} worker(s) per stage) ===")
        
        # Track when each stage will be free
        stage_free_at: Dict[str, float] = {stage: 0.0 for stage in stages}
        
        for task in tasks:
            for stage in stages:
                stage_duration = task.duration * 0.3
                
                # Stage can start when it's free AND previous stage is done
                if task == tasks[0]:
                    # First task: depends on previous stage in same task
                    prev_stages_done = stage_free_at[stages[stages.index(stage) - 1]] if stage != stages[0] else 0.0
                else:
                    # Later tasks: can start as soon as stage is free (pipeline parallelism!)
                    prev_stages_done = stage_free_at.get(stage, 0.0)
                
                start = max(stage_free_at[stage], prev_stages_done)
                end = start + stage_duration
                
                self.results.append(StageResult(
                    stage=stage,
                    task=task.name,
                    start_time=start,
                    end_time=end,
                    duration=stage_duration
                ))
                
                stage_free_at[stage] = end
                print(f"  {task.name:20} → {stage:20} [{start:6.2f}s - {end:6.2f}s]")
        
        return max(stage_free_at.values())
    
    def run_shared_pipeline(self, flood_tasks: List[Task], fire_tasks: List[Task], 
                            stages: List[str]) -> float:
        """
        Run flood and fire tasks through SHARED stages.
        Shows how reusing encoders/state-mapping avoids duplication.
        """
        print(f"\n=== SHARED PIPELINE (Flood + Fire through same stages) ===")
        
        stage_free_at: Dict[str, float] = {stage: 0.0 for stage in stages}
        all_results = []
        
        # Interleave flood and fire to show stage sharing
        all_tasks = [(t, "FLOOD") for t in flood_tasks] + [(t, "FIRE") for t in fire_tasks]
        
        for task, hazard in all_tasks:
            for stage in stages:
                stage_duration = task.duration * 0.25  # Slightly faster due to shared encoders
                
                prev_stages_done = stage_free_at[stages[stages.index(stage) - 1]] if stage != stages[0] else 0.0
                start = max(stage_free_at[stage], prev_stages_done)
                end = start + stage_duration
                
                task_label = f"{hazard[:1]}:{task.name}"
                self.results.append(StageResult(
                    stage=stage,
                    task=task_label,
                    start_time=start,
                    end_time=end,
                    duration=stage_duration
                ))
                
                stage_free_at[stage] = end
                print(f"  {task_label:20} → {stage:20} [{start:6.2f}s - {end:6.2f}s]")
        
        return max(stage_free_at.values())
    
    def print_timeline(self):
        """Print ASCII timeline of all stages."""
        if not self.results:
            return
        
        print("\n=== TIMELINE VISUALIZATION ===")
        max_time = max(r.end_time for r in self.results)
        
        stages = sorted(set(r.stage for r in self.results))
        
        for stage in stages:
            stage_tasks = [r for r in self.results if r.stage == stage]
            timeline = [' '] * int(max_time * 10 + 2)
            
            for task in stage_tasks:
                start_idx = int(task.start_time * 10)
                end_idx = int(task.end_time * 10)
                task_char = task.task[0]  # Use first char of task name
                for i in range(start_idx, min(end_idx, len(timeline))):
                    timeline[i] = '█'
            
            print(f"{stage:20} |{''.join(timeline)}|")
        
        print(f"{'Time (s)':20} |" + "".join(str(i // 10 % 10) for i in range(len(timeline))) + "|")


def demo_pipeline_advantage():
    """Demonstrate pipeline vs sequential execution."""
    
    print("=" * 80)
    print("PIPELINE PARALLELISM DEMONSTRATION")
    print("Flood & Fire Prediction Processing")
    print("=" * 80)
    
    # Define tasks and stages
    flood_tasks = [
        Task("Flood-Chunk-1", 1.0),
        Task("Flood-Chunk-2", 1.0),
        Task("Flood-Chunk-3", 1.0),
    ]
    
    fire_tasks = [
        Task("Fire-Data", 0.5),
    ]
    
    stages = [
        "Load/Parse",
        "Encode",
        "Feature-Eng",
        "Predict",
        "Aggregate"
    ]
    
    sim = PipelineSimulator()
    
    # Run sequential
    sim.results = []
    seq_time = sim.run_sequential(flood_tasks, stages)
    sim.print_timeline()
    print(f"\n📊 Sequential Total Time: {seq_time:.2f}s")
    
    # Run pipelined
    sim.results = []
    pipe_time = sim.run_pipelined(flood_tasks, stages, workers_per_stage=1)
    sim.print_timeline()
    print(f"\n📊 Pipelined Total Time: {pipe_time:.2f}s")
    
    # Run shared pipeline (both hazards)
    sim.results = []
    shared_time = sim.run_shared_pipeline(flood_tasks, fire_tasks, stages)
    sim.print_timeline()
    print(f"\n📊 Shared Pipeline Total Time: {shared_time:.2f}s")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY - Advantage of Pipelining")
    print("=" * 80)
    print(f"Sequential Execution:     {seq_time:.2f}s (baseline)")
    print(f"Pipelined Execution:      {pipe_time:.2f}s ({seq_time/pipe_time:.2f}x speedup)")
    print(f"Shared Pipeline (both):   {shared_time:.2f}s ({seq_time/shared_time:.2f}x speedup)")
    print()
    print("Key Insights:")
    print("  • Sequential: Each task waits for ALL stages to complete before next starts")
    print("  • Pipelined: While stage N processes task A, stage N+1 processes task B")
    print("  • Shared:    Reuse encoders/state-mapping across flood + fire = less overhead")
    print()
    print("Why Pipelining Wins:")
    print("  1. Stages keep working instead of idle")
    print("  2. Tasks don't stall waiting for all stages")
    print("  3. Shared resources (encoders) reduce memory & setup overhead")
    print("=" * 80)


if __name__ == '__main__':
    demo_pipeline_advantage()


def demo_pipeline_advantage_dict() -> dict:
    """Return pipeline advantage results as a dictionary for API."""
    
    # Define tasks and stages
    flood_tasks = [
        Task("Flood-Chunk-1", 1.0),
        Task("Flood-Chunk-2", 1.0),
        Task("Flood-Chunk-3", 1.0),
    ]
    
    fire_tasks = [
        Task("Fire-Data", 0.5),
    ]
    
    stages = [
        "Load/Parse",
        "Encode",
        "Feature-Eng",
        "Predict",
        "Aggregate"
    ]
    
    # Run sequential
    sim_seq = PipelineSimulator()
    seq_time = sim_seq.run_sequential(flood_tasks, stages)
    
    # Run pipelined
    sim_pipe = PipelineSimulator()
    pipe_time = sim_pipe.run_pipelined(flood_tasks, stages, workers_per_stage=1)
    
    # Run shared pipeline
    sim_shared = PipelineSimulator()
    shared_time = sim_shared.run_shared_pipeline(flood_tasks, fire_tasks, stages)
    
    # Calculate speedups
    seq_speedup = 1.0
    pipe_speedup = seq_time / pipe_time if pipe_time > 0 else 1.0
    shared_speedup = seq_time / shared_time if shared_time > 0 else 1.0
    
    return {
        'sequential': {
            'time': round(seq_time, 2),
            'speedup': round(seq_speedup, 2),
            'description': 'Each task waits for ALL stages to complete'
        },
        'pipelined': {
            'time': round(pipe_time, 2),
            'speedup': round(pipe_speedup, 2),
            'description': 'Stages process different tasks in parallel'
        },
        'shared': {
            'time': round(shared_time, 2),
            'speedup': round(shared_speedup, 2),
            'description': 'Flood + Fire share encoders & state-mapping'
        },
        'improvement': {
            'pipeline_vs_sequential': f"{((seq_time - pipe_time) / seq_time * 100):.1f}%",
            'shared_vs_sequential': f"{((seq_time - shared_time) / seq_time * 100):.1f}%"
        }
    }
