"""
MySQL Agent - Validates MySQL database
"""
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaLLM
from langchain.tools import tool
import tools


class MySQLAgent:
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
            self.check_container_tool,
            self.check_mysql_ready_tool,
            self.get_logs_tool
        ]

        # Create the agent
        self.agent = self._create_agent()

    # We define @tool decorator to turns a normal Python function into a LangChain Tool object.

    # # Issue 1: agent seding data in JSON while the calld function reading as str

    @tool
    def check_container_tool(container_name: str) -> str:
        """Check if container is running. Input: container name"""
        return tools.check_container_running(container_name)

    @tool
    def check_mysql_ready_tool(container_name: str) -> str:
        """Check if MySQL is ready to accept connections. Input: container name"""
        return tools.check_mysql_ready(container_name)

    @tool
    def get_logs_tool(container_name: str) -> str:
        """Get container logs. Input: container name"""
        return tools.get_container_logs(container_name)

    def _create_agent(self):
        """Create the MySQL validation agent"""

        prompt = PromptTemplate.from_template("""
        You are a MySQL Database Agent. Your job is to validate MySQL is working.

        Available tools:
        {tools}

        Tool names: {tool_names}

        Use this EXACT format:
        Question: the task
        Thought: what should I do
        Action: [tool name only, no extra words]
        Action Input: [JSON only]

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

    def validate(self, container_name, user, password, database):
        """Validate MySQL is ready"""
        print("\n=== MySQL Agent Starting ===")

        task = f"""
        Validate MySQL database:
        1. Check if container '{container_name}' running
        2. Check if MySQL container '{container_name}' is ready
        3. Report SUCCESS if ready, or FAILED with reason and the task is finished.

        Container: {container_name}
        """

        # print("DEBUG: Container name in Validation phase is: ", container_name)

        try:
            result = self.agent.invoke({
                "input": task
            })
            print("DEBUG: agent.invoke result =", result)

            output = result.get('output', '')

            if 'SUCCESS' in output:
                print("✓ MySQL validation: SUCCESS")
                return {"status": "success", "message": output}
            else:
                print("✗ MySQL validation: FAILED")
                return {"status": "failed", "message": output}

        except Exception as e:
            print(f"✗ MySQL Agent Error: {str(e)}")
            return {"status": "error", "message": str(e)}
