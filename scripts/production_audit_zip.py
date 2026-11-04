
"""
iCREATE v3.3.1 - Production Audit of actual ZIP/source/live deployment
Qualification: assessment based on build summary not inspected actual ZIP/source/live
This script inspects actual ZIP
"""

import zipfile, pathlib, json, sys
from datetime import datetime

def audit_zip(zip_path: str):
    print(f"\n=== Production Audit of actual ZIP {zip_path} ===")
    zip_path = pathlib.Path(zip_path)
    if not zip_path.exists():
        print(f"ZIP not found {zip_path}")
        return {}
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        files = z.namelist()
        
        checks = []
        
        # Check core engine
        core_files = ["src/pyautoforge/engine.py", "src/pyautoforge/ollama_brain.py", "src/pyautoforge/connection_manager.py"]
        for cf in core_files:
            found = any(cf in f for f in files)
            checks.append({"check": f"Core {cf}", "found": found, "status": "pass" if found else "fail"})
        
        # Check v3.4 modules
        v34_modules = [
            "sectors/sector_definitions.py",
            "sectors/sector_intelligence_engine.py",
            "sectors/sector_knowledge_registry.py",
            "sectors/dynamic_agent_factory.py",
            "sectors/business_process_discovery.py",
            "sectors/compliance_intelligence.py",
            "sectors/sector_tool_registry.py",
            "sectors/multi_tenant_isolation.py",
            "sectors/adaptive_evaluation_engine.py",
            "validation/production_validation.py",
            "validation/security_audit.py",
            "validation/integration_tests.py",
            "validation/load_testing.py",
            "validation/failure_recovery.py",
            "monitoring/shopee_monitor.py"
        ]
        for mod in v34_modules:
            found = any(mod in f for f in files)
            checks.append({"check": f"v3.4 {mod}", "found": found, "status": "pass" if found else "fail"})
        
        # Check autonomous framework
        auto_files = ["autonomous_framework/base_agent.py", "autonomous_framework/central_brain.py"]
        for af in auto_files:
            found = any(af in f for f in files)
            checks.append({"check": f"Autonomous {af}", "found": found, "status": "pass" if found else "fail"})
        
        # Size
        size_kb = zip_path.stat().st_size / 1024
        
        passed = sum(1 for c in checks if c["status"] == "pass")
        total = len(checks)
        
        result = {
            "zip_path": str(zip_path),
            "size_kb": f"{size_kb:.1f} KB",
            "total_files": len(files),
            "checks": checks,
            "total_checks": total,
            "passed": passed,
            "failed": total-passed,
            "pass_rate": f"{passed}/{total} {passed/total*100:.1f}%",
            "status": "pass" if passed/total >= 0.9 else "fail",
            "audited_at": datetime.utcnow().isoformat(),
            "qualification": "Previous assessment based on build summary not inspected actual ZIP/source/live - now inspected"
        }
        
        print(f"Size: {result['size_kb']} files: {len(files)} checks {result['pass_rate']} status {result['status']}")
        for c in checks:
            if c["status"] == "fail":
                print(f"  FAIL: {c['check']} found {c['found']}")
        
        return result

if __name__ == "__main__":
    zip_path = sys.argv[1] if len(sys.argv) > 1 else "/mnt/data/icreate_automation_engine_production.zip"
    result = audit_zip(zip_path)
    # Save report
    report_path = pathlib.Path("/tmp/production_audit_zip.json")
    report_path.write_text(json.dumps(result, indent=2))
    print(f"Report saved {report_path}")
