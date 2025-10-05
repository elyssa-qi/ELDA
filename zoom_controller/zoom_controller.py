"""
Basic Zoom Test - Verify macOS zoom accessibility
Run this first to make sure everything works
"""

import subprocess
import time

class ZoomController:
    """Control macOS screen zoom via accessibility features"""
    
    def __init__(self):
        self.current_zoom = 1.0
    
    def check_accessibility_permissions(self):
        """Check if Terminal has accessibility permissions"""
        print("Checking accessibility permissions...")
        try:
            from ApplicationServices import AXUIElementCreateSystemWide
            system_wide = AXUIElementCreateSystemWide()
            
            if system_wide:
                print("✓ Accessibility permissions granted")
                return True
            else:
                print("✗ Need accessibility permissions")
                print("Go to: System Settings → Privacy & Security → Accessibility")
                print("Add Terminal (or your IDE) to the list")
                return False
        except Exception as e:
            print(f"✗ Error checking permissions: {e}")
            return False
    
    def zoom_toggle(self):
        """Test toggling zoom on/off"""
        print("Testing zoom toggle (Command+Option+8)...")
        try:
            result = subprocess.run([
                'osascript',
                '-e',
                'tell application "System Events" to key code 28 using {command down, option down}'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✓ Zoom toggle successful")
                return True
            else:
                print(f"✗ Zoom toggle failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("✗ Command timed out")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def zoom_in(self, steps=3):
        """Zoom in with multiple steps for larger zoom"""
        print(f"\nZooming in {steps} steps (Command+Option+=)...")
        try:
            for i in range(steps):
                result = subprocess.run([
                    'osascript',
                    '-e',
                    'tell application "System Events" to key code 24 using {command down, option down}'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    print(f"✗ Zoom in step {i+1} failed: {result.stderr}")
                    return False
                
                # Small delay between steps
                import time
                time.sleep(0.05)
            
            print(f"✓ Zoom in successful ({steps} steps)")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def zoom_out(self, steps=3):
        """Zoom out with multiple steps for larger zoom reduction"""
        print(f"\nZooming out {steps} steps (Command+Option+-)...")
        try:
            for i in range(steps):
                result = subprocess.run([
                    'osascript',
                    '-e',
                    'tell application "System Events" to key code 27 using {command down, option down}'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    print(f"✗ Zoom out step {i+1} failed: {result.stderr}")
                    return False
                
                # Small delay between steps
                import time
                time.sleep(0.05)
            
            print(f"✓ Zoom out successful ({steps} steps)")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def run_full_test(self):
        """Run complete test sequence"""
        print("=" * 60)
        print("ZOOM CONTROLLER - BASIC TEST")
        print("=" * 60)
        
        # Check permissions first
        if not self.check_accessibility_permissions():
            print("\n⚠️  Fix accessibility permissions before continuing")
            return False
        
        print("\n" + "=" * 60)
        print("Running zoom tests...")
        print("=" * 60)
        
        # Test toggle
        toggle_works = self.zoom_toggle()
        time.sleep(1)
        
        # Toggle back off
        if toggle_works:
            self.zoom_toggle()
            time.sleep(1)
        
        # Test zoom in/out
        zoom_in_works = self.zoom_in()
        time.sleep(1)
        
        zoom_out_works = self.zoom_out()
        time.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Accessibility Permissions: ✓")
        print(f"Zoom Toggle: {'✓' if toggle_works else '✗'}")
        print(f"Zoom In: {'✓' if zoom_in_works else '✗'}")
        print(f"Zoom Out: {'✓' if zoom_out_works else '✗'}")
        
        all_passed = toggle_works and zoom_in_works and zoom_out_works
        
        if all_passed:
            print("\n🎉 All tests passed! You're ready to build the zoom controller.")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")
            print("\nCommon issues:")
            print("1. Accessibility permissions not granted")
            print("2. Zoom keyboard shortcuts disabled in System Settings")
            print("3. Check: System Settings → Accessibility → Zoom")
        
        return all_passed


if __name__ == "__main__":
    controller = ZoomController()
    controller.run_full_test()