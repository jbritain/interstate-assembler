from amulet_utils import *
from amulet import load_level
from amulet.api.block import Block
from amulet_nbt import StringTag

def generate_segment(source_world_path, target_world_path, entry_x, exit_x, portal_centre_y, render_distance, source_location, above_height, below_height, null_zone_width):
  # entry x is where the entry portal is
  # behind it will be terrain, stretching half the render distance (since we have to obscure half with fog anyway)
  # the same applies to the exit

  # load the level
  print("Opening source world...")
  source_world = amulet.load_level(source_world_path)
  
  # source location is the location in the world we are pulling from where the segment should start
  # specifically it is the coordinate of the centre of the portal
  # above_height is the height above the centre of the portal
  # below_height is the height below the centre of the portal

  for c in copy(
    (
      source_location[0] - render_distance * 8,
      source_location[1] + above_height,
      source_location[2] - render_distance * 8# in transition zones the segment can only be half as wide since we need two side by side
    ),
    (
      source_location[0] + render_distance * 8,
      source_location[1] - below_height,
      source_location[2] + render_distance * 8
    ),
    source_world
  ): print(f"Copying entry transition zone: {c * 100}%")

  for c in copy(
    (
      source_location[0] + render_distance * 8,
      source_location[1] + above_height,
      source_location[2] + render_distance * 16
    ),
    (
      source_location[0] + (exit_x - entry_x) - render_distance * 8,
      source_location[1] - below_height,
      source_location[2] - render_distance * 16 # in transition zones the segment can only be half as wide since we need two side by side
    ),
    source_world
  ): print(f"Copying rail segment: {c * 100}%")

  for c in copy(
    (
      source_location[0] + (exit_x - entry_x) + render_distance * 8,
      source_location[1] + above_height,
      source_location[2] - render_distance * 8 # in transition zones the segment can only be half as wide since we need two side by side
    ),
    (
      source_location[0] + (exit_x - entry_x) - render_distance * 8,
      source_location[1] - below_height,
      source_location[2] + render_distance * 8
    ),
    source_world
  ): print(f"Copying exit transition zone: {c * 100}%")

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
      exit_x,
      portal_centre_y - offset_y,
      -(null_zone_width / 2) - (render_distance * 8)
    ),
    target_world
  ): print(f"Pasting exit transition zone: {v * 100}%")

  for v in paste(
    (
      (entry_x + exit_x) / 2,
      portal_centre_y - offset_y,
      0
    ),
    target_world
  ): print(f"Pasting rail segment: {v * 100}%")

  # manual offset for entry segment on z because it's fucking weird
  for v in paste(
    (
      entry_x,
      portal_centre_y - offset_y,
      (null_zone_width / 2) + (render_distance * 8) + 2
    ),
    target_world
  ): print(f"Pasting entry transition zone: {v * 100}%")

  # place rails again along centre
  for r in place_rail((entry_x - (render_distance * 8) , portal_centre_y, 0), exit_x - entry_x, target_world): print(f"Placing rails: {r}%")

  # place rails in entry transition zone
  for r in place_rail((entry_x, portal_centre_y, (null_zone_width / 2) + (render_distance * 8)), render_distance * 8, target_world): print(f"Placing rails: {r}%")

  # place rails in exit transition zone
  for r in place_rail((exit_x - render_distance * 8, portal_centre_y, -(null_zone_width / 2) - (render_distance * 8)), render_distance * 8, target_world): print(f"Placing rails: {r}%")

  for c, t in target_world.save_iter(): print(f"Saving target world: {(c / t) * 100}%")
  target_world.close()

def place_rail(start, length, world):
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