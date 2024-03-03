from track_utils import *
from datetime import datetime
start_time = datetime.now()

target_save="C:\\Users\\Joshua\\AppData\\Roaming\\PrismLauncher\\instances\\Acid Interstate\\.minecraft\\saves\\MAIV5p1-3"
source_save_folder="C:\\Users\\Joshua\\AppData\\Roaming\\PrismLauncher\\instances\\Modern Beta\\.minecraft\\saves\\"

check_save_exists(target_save)

#generate_segment(f"{source_save_folder}farlands", f"{target_save}", 0, 1120, 64, 32, (12550868, 102, 188), 50, 50, 5, False, False)
#generate_segment(f"{source_save_folder}alpha farlands", f"{target_save}", 1120, 3360, 64, 32, (12550821, 128, 390), 20, 100, 5, False, True)
#generate_segment(f"{source_save_folder}floating islands v2", f"{target_save}", 3360, 4480, 64, 32, (94, 71, -74), 80, 20, 5, True, True)
#generate_segment(f"{source_save_folder}alpha farlands", f"{target_save}", 4480, 5600, 64, 32, (12553168, 66, 360), 50, 50, 5, True, True)
#generate_segment(f"{source_save_folder}corner farlands", f"{target_save}", 5600, 7840, 64, 32, (12550821, 97, 12551358), 50, 62, 5, True, True)
#generate_segment(f"{source_save_folder}corner farlands ii", f"{target_save}", 7840, 10067, 64, 32, (12550821, 69, -12551545), 62, 29, 5, True, True)
#generate_segment(f"{source_save_folder}corner farlands iii", f"{target_save}", 10067, 14720, 64, 32, (-12555483, 71, -12551339), 62, 12, 5, True, False)

print("Placing torches...")
with open("v5_torches_v2.json") as torchmap:
  place_torches(torchmap.read(), [3360, 4480, 5600, 7840, 10067], (64, 0), 32, f"{target_save}", 5)

end_time = datetime.now()

print(f"Assembled terrain in {end_time - start_time}")
print("Don't forget to clear the lighting cache!")