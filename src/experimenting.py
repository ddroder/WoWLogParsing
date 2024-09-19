import pandas as pd

df = pd.read_csv("test.csv")
# Assuming df is your DataFrame containing the parsed combat log data

# Define damage event types
damage_events = [
    "SPELL_DAMAGE",
    "SWING_DAMAGE",
    "RANGE_DAMAGE",
    "SPELL_PERIODIC_DAMAGE",
    "DAMAGE_SHIELD",
    "DAMAGE_SPLIT",
]

# Filter the DataFrame for damage events
print(df[["destName", "amount"]].head())
damage_df = df[df["event"].isin(damage_events)].copy()

# Ensure 'amount' field is numeric
damage_df["amount"] = pd.to_numeric(damage_df["amount"])
print(damage_df.head())
print(damage_df.columns)


# Function to determine if a unit is a player based on unit flags


def is_player_unit(flags):
    if pd.isnull(flags):
        return False
    try:
        if isinstance(flags, str):
            flags = int(flags, 0)  # Convert hex string to integer
        elif isinstance(flags, int):
            pass  # flags is already an integer
        else:
            # Attempt to convert flags to integer without specifying base
            flags = int(flags)
    except ValueError:
        return False
    except TypeError:
        return False
    # Check if the UNIT_FLAG_PLAYER_CONTROLLED (0x00000400) is set
    return (flags & 0x00000400) != 0


# Filter events where both source and destination are players
damage_df = damage_df[
    damage_df["sourceFlags"].apply(is_player_unit)
    & damage_df["destFlags"].apply(is_player_unit)
]

# Group by 'sourceName' and 'destName' and sum the 'amount'
damage_summary = (
    damage_df.groupby(["sourceName", "destName"])["amount"].sum().reset_index()
)

# Rename the columns for clarity
damage_summary.columns = ["Attacker", "Target", "Total Damage"]

# Sort the summary by 'Total Damage' in descending order
damage_summary = damage_summary.sort_values(by="Total Damage", ascending=False)

# Display the damage summary
print("Total Damage Done by Each Player to Other Players:")
print(damage_summary)
