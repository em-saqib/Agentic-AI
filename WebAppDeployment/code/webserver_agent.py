"""
WebServer Agent - Validates WordPress
"""
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaLLM
from langchain.tools import tool
import tools


class WebServerAgent:
    def __init__(self, config):
        self.config = config

        # Initialize LLM
        self.llm = ChatOllama(
            model=config['llm']['model'],
            base_url=config['llm']['url'],
            temperature=config['llm']['temperature']
        )

        # Define tools for this agent
        self.tools = [
            self.test_wordpress_url_tool,
            self.check_container_tool,
            self.get_logs_tool
        ]

        # Create the agent
        self.agent = self._create_agent()

    @tool
    def check_container_tool(container_name: str) -> str:
        """Check if container is running. Input: container name"""
        return tools.check_container_running(container_name)

    @tool
    def test_wordpress_url_tool(url: str) -> str:
        """Test if WordPress URL is accessible. Input: url"""
        return tools.test_wordpress_url(url)

    @tool
    def get_logs_tool(container_name: str) -> str:
        """Get container logs. Input: container name"""
        return tools.get_container_logs(container_name)

    def _create_agent(self):
        """Create the WordPress validation agent"""
        prompt = PromptTemplate.from_template("""
You are a WordPress Web Server Agent. Your job is to validate WordPress is working.

Available tools:
{tools}

Tool names: {tool_names}

Use this format:
Question: the task
Thought: what should I do
Action: tool to use
Action Input: tool parameters as JSON
Observation: tool result
... (repeat Thought/Action/Observation as needed)
Thought: I have completed the task
Final Answer: summary with SUCCESS or FAILED

Current task: {input}

{agent_scratchpad}
""")

        agent = create_react_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.config['agents']['verbose'],
            max_iterations=self.config['agents']['max_iterations'],
            handle_parsing_errors=True
        )

    def validate(self, container_name, wordpress_url):
        """Validate WordPress is ready"""
        print("\n=== WebServer Agent Starting ===")

        task = f"""
Validate WordPress installation:
1. Check if WordPress container '{container_name}' is running
2. Test if WordPress is accessible at '{wordpress_url}'
3. Report SUCCESS if working, or FAILED with reason and the task is finished.


Container: {container_name}
URL: {wordpress_url}
"""

        try:
            result = self.agent.invoke({
                "input": task
            })

            output = result.get('output', '')

            if 'SUCCESS' in output or 'ACCESSIBLE' in output:
                print("✓ WordPress validation: SUCCESS")
                return {"status": "success", "message": output}
            else:
                print("✗ WordPress validation: FAILED")
                return {"status": "failed", "message": output}

        except Exception as e:
            print(f"✗ WebServer Agent Error: {str(e)}")
            return {"status": "error", "message": str(e)}
