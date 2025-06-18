from backend import agents

def test_load_text_file():
    result = agents.load_text_file("fake_file.txt")
    assert result == "", "Should return empty string if file doesn't exist"

def test_run_agent_task_unknown():
    response = agents.run_agent_task("this is a test")
    assert "Answer this task" in response or "Error" in response
