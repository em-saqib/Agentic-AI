"""
Simple Tools - Essential functions for agents
"""
import subprocess
import requests
import json


def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout + result.stderr
    except Exception as e:
        return f"ERROR: {str(e)}"

def check_container_running(container_name):
    """Check if container is running"""
    try:
        container_name_dict = json.loads(container_name)
        container_name = container_name_dict.get("container_name", container_name)
    except json.JSONDecodeError:
        # Not JSON, keep as-is
        pass

    output = run_command(f"docker ps --filter name={container_name}")
    if container_name in output:
        return f"Container {container_name} is RUNNING \n"
    else:
        return f"Container {container_name} is NOT running \n"

def check_mysql_ready(container_name):
    """Check if MySQL is ready"""
    # CLI command: docker exec wp-mysql mysqladmin ping -h 127.0.0.1 -u root -proot123
    # output = run_command(f"docker exec {container_name} mysqladmin ping -h localhost")

    try:
        container_name_dict = json.loads(container_name)
        container_name = container_name_dict.get("container_name", container_name)
    except json.JSONDecodeError:
        # Not JSON, keep as-is
        pass

    output = run_command(f"docker exec {container_name} mysqladmin ping -h 127.0.0.1 -u root -proot123")
    # output = run_command(f"docker exec {container_name} mysqladmin ping -h localhost")
    print(output)

    if "alive" in output:
        return "MySQL is READY \n"
    else:
        return "MySQL is NOT ready \n"


def test_mysql_connection(container_name, user, password, database):
    """Test MySQL connection"""
    # CLI command: docker exec wp-mysql mysql -uwp_user -pwp_pass123 -e "SELECT 1;" wordpress
    # print("DEBUG from sql connection: c",container_name, user, password, database)

    print("DEBUG2: mySQL testConn Functin is called!")
    try:
        # Parse JSON input
        container_name_dict = json.loads(container_name)
        user_dict = json.loads(user)
        password_dict = json.loads(password)
        database_dict = json.loads(database)

        container_name = container_name_dict .get("container_name")
        user = user_dict.get("user")
        password = password_dict.get("password")
        database = database_dict.get("database")

    except json.JSONDecodeError:
        return "Invalid JSON input"

    print("DEBUG: Before running command")
    print(ontainer_name, user, password, database)
    cmd = f"docker exec {container_name} mysql -u{user} -p{password} -e 'SELECT 1;' {database}"
    output = run_command(cmd)
    print(output)

    if "ERROR" not in output:
        return "MySQL connection SUCCESS"
    else:
        return f"MySQL connection FAILED: {output}"


def test_wordpress_url(url):
    """Test if WordPress is accessible"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"WordPress is ACCESSIBLE at {url}"
        else:
            return f"WordPress returned status {response.status_code}"
    except Exception as e:
        return f"WordPress NOT accessible: {str(e)}"


def get_container_logs(container_name, lines=10):
    """Get container logs"""
    try:
        container_name_dict = json.loads(container_name)
        container_name = container_name_dict.get("container_name", container_name)
    except json.JSONDecodeError:
        # Not JSON, keep as-is
        pass
    output = run_command(f"docker logs --tail {lines} {container_name}")
    print("Container ", container_name, "logs :", output )
    return f"Logs extracted for containr: {container_name} \n"
