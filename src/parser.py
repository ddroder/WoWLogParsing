import re
from datetime import datetime, timezone, timedelta
import shlex
import time
import datetime
import csv
from io import StringIO
from datetime import timedelta, timezone


def resolv_power_type(pt):
    pt_map = {
        -2: "health",
        0: "mana",
        1: "rage",
        2: "focus",
        3: "energy",
        4: "pet happiness",
        5: "runes",
        6: "runic power",
    }
    return pt_map.get(pt)


def parse_unit_flag(flag):
    if isinstance(flag, str):
        f = int(flag, 0)
    else:
        f = flag

    res = []
    if f == 0:
        return res

    flag_map = {
        0x00004000: "TYPE_OBJECT",
        0x00002000: "TYPE_GUARDIAN",
        0x00001000: "TYPE_PET",
        0x00000800: "TYPE_NPC",
        0x00000400: "TYPE_PLAYER",
        0x00000200: "CONTROL_NPC",
        0x00000100: "CONTROL_PLAYER",
        0x00000040: "REACTION_HOSTILE",
        0x00000020: "REACTION_NEUTRAL",
        0x00000010: "REACTION_FRIENDLY",
        0x00000008: "AFFILIATION_OUTSIDER",
        0x00000004: "AFFILIATION_RAID",
        0x00000002: "AFFILIATION_PARTY",
        0x00000001: "AFFILIATION_MINE",
        0x08000000: "RAIDTARGET8",
        0x04000000: "RAIDTARGET7",
        0x02000000: "RAIDTARGET6",
        0x01000000: "RAIDTARGET5",
        0x00800000: "RAIDTARGET4",
        0x00400000: "RAIDTARGET3",
        0x00200000: "RAIDTARGET2",
        0x00100000: "RAIDTARGET1",
        0x00080000: "MAINASSIST",
        0x00040000: "MAINTANK",
        0x00020000: "FOCUS",
        0x00010000: "TARGET",
    }

    for k, v in flag_map.items():
        if (f & k) > 0:
            res.append(v)

    return res


def parse_school_flag(school):
    s = int(school, 0) if isinstance(school, str) else school

    res = []
    school_map = {
        0x1: "Physical",
        0x2: "Holy",
        0x4: "Fire",
        0x8: "Nature",
        0x10: "Frost",
        0x20: "Shadow",
        0x40: "Arcane",
    }

    for k, v in school_map.items():
        if (s & k) > 0:
            res.append(v)

    return res


"""
---------------------------------------------------------
Prefix Parser Set
---------------------------------------------------------
"""


class AbsorbedParser:
    def __init__(self):
        pass

    def parse(self, cols):
        obj = {}
        # Parse the absorbed spell information
        if len(cols) >= 4:
            obj["spellId"] = cols[0]
            obj["spellName"] = cols[1]
            obj["spellSchool"] = parse_school_flag(cols[2])

            # Check if the absorber is another spell or a unit
            if cols[3].startswith("0x"):
                # Absorbed by a spell (e.g., a shield)
                if len(cols) >= 7:
                    obj["absorberSpellId"] = cols[3]
                    obj["absorberSpellName"] = cols[4]
                    obj["absorberSpellSchool"] = parse_school_flag(cols[5])
                    obj["absorbAmount"] = int(cols[6])
                    if len(cols) > 7:
                        obj["critical"] = cols[7] != "nil"
                else:
                    print(f"Unexpected SPELL_ABSORBED format: {cols}")
            else:
                # Absorbed by an aura or unit
                if len(cols) >= 10:
                    obj["absorberGUID"] = cols[3]
                    obj["absorberName"] = cols[4]
                    obj["absorberFlags"] = parse_unit_flag(cols[5])
                    obj["absorberFlags2"] = parse_unit_flag(cols[6])
                    obj["absorberSpellId"] = cols[7]
                    obj["absorberSpellName"] = cols[8]
                    obj["absorberSpellSchool"] = parse_school_flag(cols[9])
                    obj["absorbAmount"] = int(cols[10])
                    if len(cols) > 11:
                        obj["critical"] = cols[11] != "nil"
                else:
                    print(f"Unexpected SPELL_ABSORBED format: {cols}")
        else:
            print(f"Unexpected SPELL_ABSORBED format: {cols}")
        return obj


class SpellParser:
    def __init__(self):
        pass

    def parse(self, cols):
        return (
            {
                "spellId": cols[0],
                "spellName": cols[1],
                "spellSchool": parse_school_flag(cols[2]),
            },
            cols[3:],
        )


class EnvParser:
    def __init__(self):
        pass

    def parse(self, cols):
        return ({"environmentalType": cols[0]}, cols[1:])


class SwingParser:
    def __init__(self):
        pass

    def parse(self, cols):
        return ({}, cols)


"""
---------------------------------------------------------
Suffix Parser Set
---------------------------------------------------------
"""


class DamageParser:
    def __init__(self):
        pass

    def parse(self, cols):
        cols = cols[8:]
        return {
            "amount": float(cols[0]),
            "overkill": cols[1],
            "school": parse_school_flag(cols[2]),
            "resisted": float(cols[3]),
            "blocked": float(cols[4]),
            "absorbed": float(cols[5]),
            "critical": (cols[6] != "nil"),
            "glancing": (cols[7] != "nil"),
            "crushing": (cols[8] != "nil"),
        }


class MissParser:
    def __init__(self):
        pass

    def parse(self, cols):
        obj = {"missType": cols[0]}
        if len(cols) > 1:
            obj["isOffHand"] = cols[1]
        if len(cols) > 2:
            obj["amountMissed"] = int(cols[2])
        return obj


class HealParser:
    def __init__(self):
        pass

    def parse(self, cols):
        cols = cols[8:]
        return {
            "amount": int(cols[0]),
            "overhealing": int(cols[1]),
            "absorbed": int(cols[2]),
            "critical": (cols[3] != "nil"),
        }


class EnergizeParser:
    def __init__(self):
        pass

    def parse(self, cols):
        cols = cols[8:]
        return {
            "amount": int(cols[0]),
            "powerType": resolv_power_type(cols[1]),
        }


class DrainParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) != 3:
            print(cols)
        return {
            "amount": int(cols[0]),
            "powerType": resolv_power_type(cols[1]),
            "extraAmount": int(cols[2]),
        }


class LeechParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) != 3:
            print(cols)
        return {
            "amount": int(cols[0]),
            "powerType": resolv_power_type(cols[1]),
            "extraAmount": int(cols[2]),
        }


class SpellBlockParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) != 3 and len(cols) != 4:
            print(cols)
        obj = {
            "extraSpellID": cols[0],
            "extraSpellName": cols[1],
            "extraSchool": parse_school_flag(cols[2]),
        }
        if len(cols) == 4:
            obj["auraType"] = cols[3]
        return obj


class ExtraAttackParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) != 1:
            print(cols)
        return {"amount": int(cols[0])}


class AuraParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) > 4:
            print(self.raw)
            print(cols)

        obj = {
            "auraType": cols[0],
        }
        # 'auraSchool': cols[1],
        # 'auraType': cols[2],

        if len(cols) >= 2:
            obj["amount"] = int(cols[1])
        if len(cols) >= 3:
            obj["auraExtra1"] = cols[2]  # Not sure this column
        if len(cols) >= 4:
            obj["auraExtra2"] = cols[3]  # Not sure this column
        return obj


class AuraDoseParser:
    def __init__(self):
        pass

    def parse(self, cols):
        obj = {
            "auraType": cols[0],
        }
        if len(cols) == 2:
            obj["powerType"] = resolv_power_type(cols[1])
        return obj


class AuraBrokenParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) != 4:
            print(cols)
        return {
            "extraSpellID": cols[0],
            "extraSpellName": cols[1],
            "extraSchool": parse_school_flag(cols[2]),
            "auraType": cols[3],
        }


class CastFailedParser:
    def __init__(self):
        pass

    def parse(self, cols):
        if len(cols) != 1:
            print(cols)
        return {
            "failedType": cols[0],
        }


"""
---------------------------------------------------------
Special Event Parser Set
---------------------------------------------------------
"""


class EnchantParser:
    def __init__(self):
        pass

    def parse(self, cols):
        return (
            {
                "spellName": cols[0],
                "itemID": cols[1],
                "itemName": cols[2],
            },
            cols,
        )


class CombatantInfoParser:
    def __init__(self):
        pass

    def parse(self, cols):
        # The columns for COMBATANT_INFO are detailed and can vary.
        # Here's a general structure based on the log data:
        obj = {
            "GUID": cols[0],
            "Strength": cols[1],
            "Agility": cols[2],
            "Stamina": cols[3],
            "Intellect": cols[4],
            "Dodge": cols[5],
            "Parry": cols[6],
            "Block": cols[7],
            "CritMelee": cols[8],
            "CritRanged": cols[9],
            "CritSpell": cols[10],
            "Speed": cols[11],
            "Lifesteal": cols[12],
            "HasteMelee": cols[13],
            "HasteRanged": cols[14],
            "HasteSpell": cols[15],
            "Avoidance": cols[16],
            "Mastery": cols[17],
            "VersatilityDamageDone": cols[18],
            "VersatilityHealingDone": cols[19],
            "VersatilityDamageTaken": cols[20],
            "Armor": cols[21],
            "CurrentSpecID": cols[22],
            "Talents": cols[23],
            "PVP Talents": cols[24],
            "ArtifactTraits": cols[25],
            "Equipment": cols[26],
            "InterestingAuras": cols[27],
            "Stats": cols[28:],
        }
        return obj


class ArenaMatchParser:
    def __init__(self):
        pass

    def parse(self, cols):
        # The columns for ARENA_MATCH_START are:
        # ['ARENA_MATCH_START', 'mapID', 'matchDuration', 'teamSize', 'rated']
        # Adjust the parsing logic based on the actual data
        obj = {
            "mapID": cols[0],
            "matchDuration": cols[1],
            "teamSize": cols[2],
            "rated": cols[3],
        }
        return obj


class EncountParser:
    def __init__(self):
        pass

    def parse(self, cols):
        obj = {
            "encounterID": cols[0],
            "encounterName": cols[1],
            "difficultyID": cols[2],
            "groupSize": cols[3],
        }
        if len(cols) == 5:
            obj["success"] = cols[4] == "1"
        return obj


class VoidParser:
    def __init__(self):
        pass

    def parse(self, cols):
        return ({}, cols)


class VoidSuffixParser:
    def __init__(self):
        pass

    def parse(self, cols):
        return {}


class Parser:
    def __init__(self):
        self.player_classes = {}
        self.ev_prefix = {
            "SWING": SwingParser(),
            "SPELL_BUILDING": SpellParser(),
            "SPELL_PERIODIC": SpellParser(),
            "SPELL": SpellParser(),
            "RANGE": SpellParser(),
            "ENVIRONMENTAL": EnvParser(),
        }
        self.ev_suffix = {
            "_DAMAGE": DamageParser(),
            "_MISSED": MissParser(),
            "_HEAL": HealParser(),
            "_ENERGIZE": EnergizeParser(),
            "_DRAIN": DrainParser(),
            "_LEECH": LeechParser(),
            "_INTERRUPT": SpellBlockParser(),
            "_DISPEL": SpellBlockParser(),
            "_DISPEL_FAILED": SpellBlockParser(),
            "_STOLEN": SpellBlockParser(),
            "_EXTRA_ATTACKS": ExtraAttackParser(),
            "_AURA_APPLIED": AuraParser(),
            "_AURA_REMOVED": AuraParser(),
            "_AURA_APPLIED_DOSE": AuraDoseParser(),
            "_AURA_REMOVED_DOSE": AuraDoseParser(),
            "_AURA_REFRESH": AuraDoseParser(),
            "_AURA_BROKEN": AuraParser(),
            "_AURA_BROKEN_SPELL": AuraBrokenParser(),
            "_CAST_START": VoidSuffixParser(),
            "_CAST_SUCCESS": VoidSuffixParser(),
            "_CAST_FAILED": CastFailedParser(),
            "_INSTAKILL": VoidSuffixParser(),
            "_DURABILITY_DAMAGE": VoidSuffixParser(),
            "_DURABILITY_DAMAGE_ALL": VoidSuffixParser(),
            "_CREATE": VoidSuffixParser(),
            "_SUMMON": VoidSuffixParser(),
            "_RESURRECT": VoidSuffixParser(),
            "_ABSORBED": AbsorbedParser(),
        }
        self.sp_event = {
            "DAMAGE_SHIELD": (SpellParser(), DamageParser()),
            "DAMAGE_SPLIT": (SpellParser(), DamageParser()),
            "DAMAGE_SHIELD_MISSED": (SpellParser(), MissParser()),
            "ENCHANT_APPLIED": (EnchantParser(), VoidSuffixParser()),
            "ENCHANT_REMOVED": (EnchantParser(), VoidSuffixParser()),
            "PARTY_KILL": (VoidParser(), VoidSuffixParser()),
            "UNIT_DIED": (VoidParser(), VoidSuffixParser()),
            "UNIT_DESTROYED": (VoidParser(), VoidSuffixParser()),
        }
        self.enc_event = {
            "ENCOUNTER_START": EncountParser(),
            "ENCOUNTER_END": EncountParser(),
            "ARENA_MATCH_START": ArenaMatchParser(),
            "ARENA_MATCH_END": ArenaMatchParser(),
            "COMBATANT_INFO": CombatantInfoParser(),
        }

    def get_class_name_from_spec_id(self, spec_id):
        spec_to_class_map = {
            # Death Knight
            250: "Death Knight",  # Blood
            251: "Death Knight",  # Frost
            252: "Death Knight",  # Unholy
            # Demon Hunter
            577: "Demon Hunter",  # Havoc
            581: "Demon Hunter",  # Vengeance
            # Druid
            102: "Druid",  # Balance
            103: "Druid",  # Feral
            104: "Druid",  # Guardian
            105: "Druid",  # Restoration
            # Hunter
            253: "Hunter",  # Beast Mastery
            254: "Hunter",  # Marksmanship
            255: "Hunter",  # Survival
            # Mage
            62: "Mage",  # Arcane
            63: "Mage",  # Fire
            64: "Mage",  # Frost
            # Monk
            268: "Monk",  # Brewmaster
            270: "Monk",  # Mistweaver
            269: "Monk",  # Windwalker
            # Paladin
            65: "Paladin",  # Holy
            66: "Paladin",  # Protection
            70: "Paladin",  # Retribution
            # Priest
            256: "Priest",  # Discipline
            257: "Priest",  # Holy
            258: "Priest",  # Shadow
            # Rogue
            259: "Rogue",  # Assassination
            260: "Rogue",  # Outlaw
            261: "Rogue",  # Subtlety
            # Shaman
            262: "Shaman",  # Elemental
            263: "Shaman",  # Enhancement
            264: "Shaman",  # Restoration
            # Warlock
            265: "Warlock",  # Affliction
            266: "Warlock",  # Demonology
            267: "Warlock",  # Destruction
            # Warrior
            71: "Warrior",  # Arms
            72: "Warrior",  # Fury
            73: "Warrior",  # Protection
            # Evoker (introduced in Dragonflight)
            1467: "Evoker",  # Devastation
            1468: "Evoker",  # Preservation
            1473: "Evoker",  # Augmentation
        }
        return spec_to_class_map.get(spec_id, "Unknown")

    def parse_combatant_info(self, cols):
        event = cols[0]
        player_guid = cols[1]
        # The stats are fixed fields; parse up to 'Armor'
        fixed_fields = cols[2:23]  # Strength to Armor
        current_spec_id = int(cols[23])

        class_name = self.get_class_name_from_spec_id(current_spec_id)
        self.player_classes[player_guid] = class_name

        # The rest of the fields are variable-length lists; parse them if needed
        # ...

        return {
            "timestamp": ts,
            "event": event,
            "playerGUID": player_guid,
            "currentSpecID": current_spec_id,
            "className": class_name,
            # Include other fields if desired
        }

    def parse_line(self, line):
        # Strip the line and split it into date, time, and the rest
        terms = line.strip().split(None, 2)
        if len(terms) < 3:
            raise Exception("invalid format, " + line)

        # Extract date and full time string (which may include milliseconds and timezone)
        date_str = terms[0]  # e.g., '9/18/2024'
        time_str_full = terms[1]  # e.g., '23:47:17.936-4'

        # Parse date
        date_parts = list(map(int, date_str.split("/")))  # [month, day, year]

        # Use regex to split time, milliseconds, and timezone offset
        time_pattern = r"^(\d{2}:\d{2}:\d{2})(?:\.(\d+))?([+-]\d+)?$"
        match = re.match(time_pattern, time_str_full)
        if not match:
            raise Exception("Invalid time format: " + time_str_full)

        time_part = match.group(1)  # '23:47:17'
        ms_part = match.group(2)  # '936' or None
        tz_part = match.group(3)  # '-4' or None

        # Build datetime object
        dt_str = "{year}-{month:02d}-{day:02d} {time}".format(
            year=date_parts[2], month=date_parts[0], day=date_parts[1], time=time_part
        )
        dt_format = "%Y-%m-%d %H:%M:%S"
        dt = datetime.datetime.strptime(dt_str, dt_format)

        # Add milliseconds if present
        if ms_part:
            ms_fraction = int(ms_part) / (10 ** len(ms_part))
            dt += timedelta(seconds=ms_fraction)

        # Adjust for timezone if present
        if tz_part:
            tz_offset_hours = int(tz_part)
            tz_offset = timedelta(hours=tz_offset_hours)
            dt = dt.replace(tzinfo=timezone(tz_offset))
        else:
            dt = dt.replace(tzinfo=timezone.utc)

        # Get UNIX timestamp
        ts = dt.timestamp()

        # Parse the rest of the line using csv.reader to handle commas and quoted strings
        csv_txt = terms[2].strip()
        reader = csv.reader(StringIO(csv_txt))
        cols = next(reader)

        obj = self.parse_cols(ts, cols)

        return obj

    def parse_line(self, line):
        terms = line.strip().split(" ")
        if len(terms) < 4:
            raise Exception("invalid format, " + line)

        # Extract date and full time string (which may include milliseconds and timezone)
        date_str = terms[0]  # e.g., '9/18/2024'
        time_str_full = terms[1]  # e.g., '23:47:17.936-4'

        date_parts = list(map(int, date_str.split("/")))  # [month, day, year]

        # Use regex to split time, milliseconds, and timezone offset
        time_pattern = r"^(\d{2}:\d{2}:\d{2})(?:\.(\d+))?([+-]\d+)?$"
        match = re.match(time_pattern, time_str_full)
        if not match:
            raise Exception("Invalid time format: " + time_str_full)

        time_part = match.group(1)  # '23:47:17'
        ms_part = match.group(2)  # '936' or None
        tz_part = match.group(3)  # '-4' or None

        # Build datetime object
        dt_str = "{year}-{month:02d}-{day:02d} {time}".format(
            year=date_parts[2], month=date_parts[0], day=date_parts[1], time=time_part
        )
        dt_format = "%Y-%m-%d %H:%M:%S"
        dt = datetime.datetime.strptime(dt_str, dt_format)

        # Add milliseconds if present
        if ms_part:
            ms_fraction = int(ms_part) / (10 ** len(ms_part))
            dt += timedelta(seconds=ms_fraction)

        # Adjust for timezone if present
        if tz_part:
            tz_offset_hours = int(tz_part)
            tz_offset = timedelta(hours=tz_offset_hours)
            dt = dt.replace(tzinfo=timezone(tz_offset))
        else:
            dt = dt.replace(tzinfo=timezone.utc)

        # Get UNIX timestamp
        ts = dt.timestamp()

        # Parse the rest of the line
        csv_txt = " ".join(terms[3:]).strip()
        splitter = shlex.shlex(csv_txt, posix=True)
        splitter.whitespace = ","
        splitter.whitespace_split = True
        cols = list(splitter)
        obj = self.parse_cols(ts, cols)

        return obj

    def parse_cols(self, ts, cols):
        event = cols[0]

        if event == "COMBATANT_INFO":
            return self.parse_combatant_info(cols)
        if self.enc_event.get(event):
            # Handling encounter events
            obj = {
                "timestamp": ts,
                "event": event,
            }
            obj.update(self.enc_event[event].parse(cols[1:]))
            return obj

        elif event == "SPELL_ABSORBED":
            # Special handling for SPELL_ABSORBED
            obj = {
                "timestamp": ts,
                "event": event,
                "sourceGUID": cols[1],
                "sourceName": cols[2],
                "sourceFlags": parse_unit_flag(cols[3]),
                "sourceFlags2": parse_unit_flag(cols[4]),
                "destGUID": cols[5],
                "destName": cols[6],
                "destFlags": parse_unit_flag(cols[7]),
                "destFlags2": parse_unit_flag(cols[8]),
            }
            # The rest of cols[9:] is specific to SPELL_ABSORBED
            remain = cols[9:]
            obj.update(AbsorbedParser().parse(remain))
            return obj

        else:
            if len(cols) < 9:
                raise Exception("invalid format, " + repr(cols))

            obj = {
                "timestamp": ts,
                "event": event,
                "sourceGUID": cols[1],
                "sourceName": cols[2],
                "sourceFlags": parse_unit_flag(cols[3]),
                "sourceFlags2": parse_unit_flag(cols[4]),
                "destGUID": cols[5],
                "destName": cols[6],
                "destFlags": parse_unit_flag(cols[7]),
                "destFlags2": parse_unit_flag(cols[8]),
            }

            source_guid = obj.get("sourceGUID")
            dest_guid = obj.get("destGUID")

            obj["sourceClass"] = self.player_classes.get(source_guid)
            obj["destClass"] = self.player_classes.get(dest_guid)

            suffix = ""
            prefix_psr = None
            suffix_psr = None

            matches = []
            for k, p in self.ev_prefix.items():
                if event.startswith(k):
                    matches.append(k)

            if len(matches) > 0:
                prefix = max(matches, key=len)
                prefix_psr = self.ev_prefix[prefix]
                suffix = event[len(prefix) :]
                suffix_psr = self.ev_suffix.get(suffix)
                if suffix_psr is None:
                    raise Exception(f"Unknown suffix '{suffix}' in event '{event}'")
            else:
                psrs = self.sp_event.get(event)
                if psrs:
                    (prefix_psr, suffix_psr) = psrs
                else:
                    raise Exception("Unknown event format, " + repr(cols))

            if prefix_psr is None or suffix_psr is None:
                raise Exception("Unknown event format, " + repr(cols))

            (res, remain) = prefix_psr.parse(cols[9:])
            obj.update(res)
            suffix_psr.raw = cols
            obj.update(suffix_psr.parse(remain))

            return obj

    def read_file(self, fname):
        with open(fname, "r") as f:
            for line in f:
                yield self.parse_line(line)


if __name__ == "__main__":
    import sys

    p = Parser()
    for arg in sys.argv[1:]:
        for a in p.read_file(arg):
            pass
