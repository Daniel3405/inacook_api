import os
import subprocess
import sys

def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Scripts to explicitly exclude
    excluded = [
        'test_endpoints.py',
        'inspect_db.py',
        'setup_full.py', # Exclude this script itself
        '__init__.py'
    ]
    
    # Priority order: these should run first to establish dependencies (Roles -> Units -> Users)
    priority_order = [
        'populate_units.py',           # Base data
        'crear_roles.py',              # Base data
        'create_test_admin.py',        # User
        'create_test_profesor.py',     # User
        'create_test_estudiante.py',   # User
    ]
    
    # Get all python files in the directory
    all_files = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
    
    # Filter out excluded files
    candidates = [f for f in all_files if f not in excluded]
    
    queue = []
    
    # 1. Enqueue priority scripts first
    for script in priority_order:
        if script in candidates:
            queue.append(script)
            candidates.remove(script)
            
    # 2. Enqueue remaining scripts (like create_recetas_via_urls.py)
    # Sorted alphabetically to ensure deterministic order
    for script in sorted(candidates):
        queue.append(script)
        
    print(f"--- Full Setup Script ---")
    print(f"Scripts to run: {len(queue)}")
    for s in queue:
        print(f" - {s}")
    print(f"Excluded: {excluded}\n")
    
    print("Starting execution...\n")

    for script_name in queue:
        script_path = os.path.join(scripts_dir, script_name)
        print(f"--> Running {script_name}...")
        
        try:
            # Execute the script in a subprocess
            result = subprocess.run([sys.executable, script_path], check=False)
            
            if result.returncode == 0:
                print(f"--> {script_name} COMPLETED SUCCESSFULLLY.\n")
            else:
                print(f"!! {script_name} FAILED with exit code {result.returncode}.\n")
                
        except Exception as e:
            print(f"!! Unexpected error executing {script_name}: {e}\n")

    print("--- Setup Process Complete ---")
    print("Note: If 'create_recetas_via_urls.py' failed, ensure your backend server is running (python manage.py runserver).")

if __name__ == '__main__':
    main()
