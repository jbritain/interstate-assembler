from amulet_utils import *
from amulet import load_level
from amulet.api.block import Block
from amulet_nbt import StringTag
import math
import json


def check_save_exists(path):
  world = amulet.load_level(path)
  print(f"World {path} exists")
  world.close()

def generate_segment(source_world_path, target_world_path, entry_x, exit_x, portal_centre_y, render_distance, source_location, above_height, below_height, null_zone_width, do_entry=True, do_exit=True):
  # entry x is where the entry portal is
  # behind it will be terrain, stretching half the render distance (since we have to obscure half with fog anyway)
  # the same applies to the exit

  length = exit_x - entry_x

  # load the level
  print("Opening source world...")
  source_world = amulet.load_level(source_world_path)
  
  # source location is the location in the world we are pulling from where the segment should start
  # specifically it is the coordinate of the centre of the portal
  # above_height is the height above the centre of the portal
  # below_height is the height below the centre of the portal

  for c in copy(
    (
      source_location[0] - (render_distance * 8 if do_entry else 0),
      source_location[1] + above_height,
      source_location[2] - render_distance * (8 if do_entry else 16)# in transition zones the segment can only be half as wide since we need two side by side
    ),
    (
      source_location[0] + render_distance * 8,
      source_location[1] - below_height,
      source_location[2] + render_distance * (8 if do_entry else 16)
    ),
    source_world
  ): print(f"Copying entry transition zone: {round(c * 100)}%", end="\r")
  print()

  for c in copy(
    (
      source_location[0] + render_distance * 8,
      source_location[1] + above_height,
      source_location[2] + render_distance * 16
    ),
    (
      source_location[0] + length - render_distance * 8,
      source_location[1] - below_height,
      source_location[2] - render_distance * 16
    ),
    source_world
  ): print(f"Copying rail segment: {round(c * 100)}%", end="\r")
  print()

  for c in copy(
    (
      source_location[0] + length + (render_distance * 8 if do_exit else 0),
      source_location[1] + above_height,
      source_location[2] - render_distance * (8 if do_exit else 16) # in transition zones the segment can only be half as wide since we need two side by side
    ),
    (
      source_location[0] + length - render_distance * 8,
      source_location[1] - below_height,
      source_location[2] + render_distance * (8 if do_exit else 16)
    ),
    source_world
  ): print(f"Copying exit transition zone: {round(c * 100)}%", end="\r")
  print()

  print("Closing source world...")
  source_world.close()

  print("Opening target world...")
  target_world = amulet.load_level(target_world_path)

  # we now paste the exit zone, then the rail segment, then the entry zone

  # exit zone goes on the left

  # we need to find the offset to paste from to align the rail on the y axis because amulet always pastes from the centre
  segment_height = (above_height + below_height + 1)
  segment_centre_y = segment_height / 2 # the vertical centre of the segment
  segment_portal_centre_y = below_height + 1
  offset_y = segment_portal_centre_y - segment_centre_y

  for v in paste(
    (
      exit_x - (0 if do_exit else render_distance * 4),
      portal_centre_y - offset_y,
    (-(null_zone_width / 2) - (render_distance * 8)) if do_exit else 0 
    ),
    target_world
  ): print(f"Pasting exit transition zone: {round(v * 100)}%", end="\r")
  print()

  for v in paste(
    (
      (entry_x + exit_x) / 2,
      portal_centre_y - offset_y,
      0
    ),
    target_world
  ): print(f"Pasting rail segment: {round(v * 100)}%", end="\r")
  print()

  for v in paste(
    (
      entry_x + (0 if do_entry else render_distance * 4),
      portal_centre_y - offset_y,
      ((null_zone_width / 2) + (render_distance * 8) + 1) if do_entry else 0 # offset by one for some reason
    ),
    target_world
  ): print(f"Pasting entry transition zone: {round(v * 100)}%", end="\r")
  print()

  # place rails in entry transition zone
  for r in place_rail((
    entry_x,
    portal_centre_y,
    (math.ceil(null_zone_width / 2) + (render_distance * 8)) if do_entry else 0
  ), render_distance * 8, target_world): print(f"Placing entry rails: {round(r * 100)}%", end="\r")
  print()
  
   # place rails along centre
  for r in place_rail((
    entry_x - (render_distance *  8), 
    portal_centre_y,
    0
  ), length + (render_distance * 16), target_world
  ): print(f"Placing main rails: {round(r * 100)}%", end="\r")
  print()

  for r in place_rail((
    exit_x - (render_distance * 8),
    portal_centre_y,
    (-math.floor(null_zone_width / 2) - (render_distance * 8)) if exit else 0
  ), render_distance * 8, target_world): print(f"Placing exit rails: {round(r * 100)}%", end="\r")
  print()

  for c, t in target_world.save_iter(): print(f"Saving target world: {round((c / t) * 100)}%", end="\r")
  print()
  target_world.close()

def place_rail(start, length, world):
  print(f"Placing rails between {start[0]} and {start[0] + length} at z {start[2]} and y {start[1]}")
  try:
    yield from fill(
      (
        start[0],
        start[1] - 2,
        start[2]
      ),
      (
        start[0] + length,
        start[1] - 1,
        start[2] + 1
      ),
      Block("minecraft", "redstone_block"),
      world
    )

    yield from fill(
      (
        start[0],
        start[1] - 1,
        start[2]
      ),
      (
        start[0] + length,
        start[1],
        start[2] + 1
      ),
      Block(
        "minecraft",
        "powered_rail",
        {
            "powered": StringTag("true"),
            "shape": StringTag("east_west")
        }
      ),
      world
    )

    yield from fill(
      (
        start[0],
        start[1],
        start[2]
      ),
      (
        start[0] + length,
        start[1] + 1,
        start[2] + 1
      ),
      Block("minecraft", "air"),
      world
    )
  except Exception as e:
        print(f"Error during fill: {e}")

def place_torches(torchmap, portals, portal_centre, render_distance, world_path, null_zone_width):
  world = amulet.load_level(world_path)
  torches = json.loads(torchmap)
  print("Placing torches...")
  for torch in torches:
    modified_portal_centre_z = portal_centre[1]
    for portal in portals:
      if abs(portal - torch["x"]) < render_distance * 8:
        if (torch["x"]) < portal:
          modified_portal_centre_z -= math.floor(null_zone_width / 2) + render_distance * 8
        else:
          modified_portal_centre_z += math.ceil(null_zone_width / 2) + render_distance * 8

    place_torch(torch, (portal_centre[0], modified_portal_centre_z), world)
  world.save()
  world.close()

def place_torch(torch, portal_centre, world):
  x = torch["x"]
  height = torch["height"]
  side = torch["side"]

  if height == "1":
    if side == "l" or side == "b":
      set_block((x, portal_centre[0] - 2, portal_centre[1] - 1), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0] - 1, portal_centre[1] - 1), Block("minecraft", "torch"), world)
    if side == "r" or side == "b":
      set_block((x, portal_centre[0] - 2, portal_centre[1] + 1), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0] - 1, portal_centre[1] + 1), Block("minecraft", "torch"), world)
  elif height == "2":
    if side == "l" or side == "b":
      set_block((x, portal_centre[0] - 1, portal_centre[1] - 1), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0] - 2, portal_centre[1] - 1), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0], portal_centre[1] - 1), Block("minecraft", "torch"), world)
    if side == "r" or side == "b":
      set_block((x, portal_centre[0] - 1, portal_centre[1] + 1), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0] - 2, portal_centre[1] + 1), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0], portal_centre[1] + 1), Block("minecraft", "torch"), world)
  else:
    if side == "l" or side == "b":
      set_block((x, portal_centre[0], portal_centre[1] - 2), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0], portal_centre[1] - 1), Block("minecraft", "wall_torch", {"facing": StringTag("south")}), world)
    if side == "r" or side == "b":
      set_block((x, portal_centre[0], portal_centre[1] + 2), Block("minecraft", "cobblestone"), world)
      set_block((x, portal_centre[0], portal_centre[1] + 1), Block("minecraft", "wall_torch", {"facing": StringTag("north")}), world)