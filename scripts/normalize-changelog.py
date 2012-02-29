# Encoding: UTF-8
"""Normalize, somewhat, the move changelog.

This is an unmaintained one-shot script, only included in the repo for reference.

Reads from the DB, writes a CSV file.
"""

import os
import csv
import subprocess

from pokedex.db import tables, connect, util
from pokedex.defaults import get_default_csv_dir

session = connect()

query = session.query(tables.VersionGroup)
query = query.order_by(tables.VersionGroup.id)
last_version_group = query[-1]

version_groups = list(session.query(tables.VersionGroup))

version_groups.sort(key=lambda vg: vg.order)

out_path = os.path.join(get_default_csv_dir(), 'move_mechanics.csv')
print 'Writing to', out_path
with open(out_path, 'w') as outfile:
    meta_fields = ['move_id', 'version_group_id']
    data_fields = ['type_id', 'power', 'pp', 'accuracy', 'priority',
        'target_id', 'damage_class_id', 'effect_id', 'effect_chance']
    fields = meta_fields + data_fields
    writer = csv.DictWriter(outfile, fields, lineterminator='\n')
    writer.writeheader()
    for move in session.query(tables.Move):
        data = dict(move_id=move.id)
        for field in data_fields:
            data[field] = getattr(move, field)

        changelog = {c.changed_in: c for c in move.changelog}
        for version_group in version_groups:
            if version_group.generation_id < move.generation_id:
                continue
            data['version_group_id'] = version_group.id
            writer.writerow(data)
            try:
                change = changelog[version_group]
            except KeyError:
                pass
            else:
                for field in data_fields:
                    changed_datum = getattr(change, field, None)
                    if changed_datum is not None:
                        data[field] = changed_datum
