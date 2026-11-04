
import asyncio
import sys
sys.path.insert(0, "src")
from pyautoforge.agents.autonomous_framework import UniversalAutonomousAgentFramework

async def test():
    framework = UniversalAutonomousAgentFramework()
    
    # Test 1: Automated online store
    print("\n=== Test 1: Gusto kong magkaroon ng automated online store ===")
    result1 = await framework.execute_client_request(
        client_request="Gusto kong magkaroon ng automated online store",
        client_id="test_client_1",
        budget="$500",
        deadline="1 week"
    )
    print(f"Result: {result1['final_status']} - {result1['verification']}")
    print(f"Agents executed: {len(result1['execution_results'])}")
    
    # Test 2: Automated business management
    print("\n=== Test 2: I want an automated business management system ===")
    result2 = await framework.execute_client_request(
        client_request="I want an automated business management system",
        client_id="test_client_2",
        budget="$1000",
        deadline="2 weeks"
    )
    print(f"Result: {result2['final_status']} - {result2['verification']}")
    
    # Test 3: Price monitoring
    print("\n=== Test 3: Monitor 100 Shopee products hourly ===")
    result3 = await framework.execute_client_request(
        client_request="Monitor 100 Shopee products hourly and alert price drops",
        client_id="test_client_3",
        budget="$200/mo",
        deadline="3 days"
    )
    print(f"Result: {result3['final_status']} - {result3['verification']}")
    
    print("\n=== All tests completed ===")
    print(f"Framework version: {framework.version}")
    print(f"Total agents: {len(framework.agents)} + Central Brain")
    print(f"Autonomy levels: L0 Observe, L1 Recommend, L2 Execute, L3 Adapt, L4 Optimize")
    print(f"Universal Constitution: 12 rules - Objective First, Independent Thinking, No Hallucination, etc")

if __name__ == "__main__":
    asyncio.run(test())
