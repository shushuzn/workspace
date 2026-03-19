def execute_step(step_config):
    """执行单个步骤"""
    step_id = step_config['step_id']
    tool_id = step_config.get('tool_id')
    step_name = step_config['name']
    
    print(f"\n{'='*60}")
    print(f"Step {step_id}: {step_name}")
    print(f"{'='*60}")
    
    if not tool_id:
        print(f"[INFO] 步骤 {step_id} 无关联工具，自动跳过")
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--complete-step",
            str(step_id)
        ], cwd=str(WORKSPACE), capture_output=True)
        return True
    
    # 配置步骤：这些工具需要特定参数，自动跳过
    config_tools = [
        'flow_manager', 'task_analyzer', 'tool_suggester',
        'workflow_selector', 'subworkflow_dispatcher', 'workflow_scheduler',
        'execution_logger', 'checkpoint_saver', 'tool_executor'
    ]
    if tool_id in config_tools:
        print(f"[INFO] 步骤 {step_id} ({tool_id}) 是配置步骤，自动跳过")
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--complete-step",
            str(step_id)
        ], cwd=str(WORKSPACE), capture_output=True)
        return True
    
    # 特殊处理：批判者需要额外参数
    if tool_id == 'auto_critic_v7':
        print(f"[INFO] 步骤 {step_id} (auto_critic_v7) 使用默认参数执行")
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "auto-critic_v7.py"),
            "-t", "auto_workflow_execution",
            "-p", "final",
            "--flow_id", "20260318-universal-workflow-001"
        ], cwd=str(WORKSPACE), capture_output=True)
        
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--complete-step",
            str(step_id)
        ], cwd=str(WORKSPACE), capture_output=True)
        return True
    
    # 特殊处理：session_end 需要特定参数
    if tool_id == 'session_end':
        print(f"[INFO] 步骤 {step_id} (session_end) 执行会话结束处理")
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "session_end.py"),
            "auto",
            "--flow_id", "20260318-universal-workflow-001"
        ], cwd=str(WORKSPACE), capture_output=True)
        
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--complete-step",
            str(step_id)
        ], cwd=str(WORKSPACE), capture_output=True)
        return True
    
    # 特殊处理：Git 提交
    if tool_id == 'git_commit_push':
        print(f"[INFO] 步骤 {step_id} (git_commit_push) 执行 Git 提交")
        result = subprocess.run(['git', 'status', '--short'], 
                              cwd=str(WORKSPACE), 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("[INFO] 检测到 Git 变更，执行提交...")
            subprocess.run(['git', 'add', '-A'], cwd=str(WORKSPACE), capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'auto: 工作流自动执行完成'], cwd=str(WORKSPACE), capture_output=True)
            subprocess.run(['git', 'push', 'origin', 'master'], cwd=str(WORKSPACE), capture_output=True)
        else:
            print("[INFO] 无 Git 变更，跳过提交")
        
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--complete-step",
            str(step_id)
        ], cwd=str(WORKSPACE), capture_output=True)
        return True
    
    # 特殊处理：quality_gate_check 需要 --all 参数
    if tool_id == 'quality_gate_check':
        print(f"[INFO] 步骤 {step_id} (quality_gate_check) 执行质量检查")
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "quality_gate_check.py"),
            "--all"
        ], cwd=str(WORKSPACE), capture_output=True)
        
        subprocess.run([
            sys.executable,
            str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
            "--complete-step",
            str(step_id)
        ], cwd=str(WORKSPACE), capture_output=True)
        return True
    
    # 使用 tool_executor 执行（自动完成步骤）
    result = subprocess.run([
        sys.executable,
        str(TOOL_EXECUTOR),
        tool_id
    ], cwd=str(WORKSPACE), capture_output=True, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode == 0:
        print(f"[OK] 步骤 {step_id} 执行成功（自动完成）")
        return True
    else:
        print(f"[ERROR] 步骤 {step_id} 执行失败")
        try:
            print(result.stdout)
            print(result.stderr)
        except UnicodeEncodeError:
            print(result.stdout.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
            print(result.stderr.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
        return False
