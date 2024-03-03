import amulet
# for some fucking reason amulet.api.structure doesn't resolve because they just didn't include it in the init.py
# I'm sure there's a great reason for this, be nice if it was WRITTEN DOWN SOMEWHERE
from amulet.api import structure

def copy(start, end, world) -> None:
  dimension=world.dimensions[0]
  # get area and copy to clipboard
  selection = amulet.api.selection.SelectionBox(
    start,
    end
  )
  structure = yield from world.extract_structure_iter(amulet.api.selection.SelectionGroup([selection]), dimension)
  amulet.api.structure.structure_cache.add_structure(structure, structure.dimensions[0])

def delete(start, end, world):
  yield from fill(start, end, amulet.api.block.UniversalAirBlock, world)

def fill(start, end, block, world):
  dimension=world.dimensions[0]
  selection = amulet.api.selection.SelectionBox(
    start,
    end
  )

  # shamelessly stolen from amulet editor source code since their documentation is awful
  # https://github.com/Amulet-Team/Amulet-Map-Editor/blob/0.10/amulet_map_editor/programs/edit/plugins/operations/stock_plugins/internal_operations/delete.py
  # in fact even then, some of the functions the editor code calls DON'T EVEN FUCKING EXIST ANYMORE so I had to change them
  # I wish this software was closed source so I could complain about it and still take the moral high ground \s

  iter_count = len(list(world.get_coord_box(dimension, selection, False)))
  count = 0
  internal_id = world.block_palette.get_add_block(block)

  for chunk, slices, _ in world.get_chunk_slice_box(dimension, selection, False):
    chunk.blocks[slices] = internal_id

    chunk_x, chunk_z = chunk.coordinates
    chunk_x *= 16
    chunk_z *= 16
    x_min = chunk_x + slices[0].start
    y_min = slices[1].start
    z_min = chunk_z + slices[2].start
    x_max = chunk_x + slices[0].stop
    y_max = slices[1].stop
    z_max = chunk_z + slices[2].stop

    for x, y, z in list(chunk.block_entities.keys()):
        if x_min <= x < x_max and y_min <= y < y_max and z_min <= z < z_max:
            chunk.block_entities.pop((x, y, z))

    chunk.changed = True
    count += 1
    yield count / iter_count
   

def cut(start, end, world):
  dimension=world.dimensions[0]
  yield from copy(start, end, dimension)
  yield from delete(start, end, dimension)

def paste(location, world):
  dimension=world.dimensions[0]
  # note that the paste function pastes relative to the centre
  structure, structure_dimension = amulet.api.structure.structure_cache.pop_structure()
  yield from world.paste_iter(structure, structure_dimension, structure.bounds(structure_dimension), dimension, location, include_entities=False)

def set_block(location, block, world):
  world.set_version_block(
    location[0],
    location[1],
    location[2],
    "minecraft:overworld",
    ("java", (1, 20, 2)),
    block
  )