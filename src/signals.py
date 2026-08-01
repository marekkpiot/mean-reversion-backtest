import pandas as pd


def generate_target_positions(
    zscore: pd.Series,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.5,
) -> pd.Series:
    """
    Transforme un z-score en positions de pair trading.

    Positions :
        +1 : acheter le spread
             acheter SPY et vendre IVV

         0 : aucune position

        -1 : vendre le spread
             vendre SPY et acheter IVV
    """

    if entry_threshold <= 0:
        raise ValueError(
            "Le seuil d'entrée doit être positif."
        )

    if exit_threshold < 0:
        raise ValueError(
            "Le seuil de sortie ne peut pas être négatif."
        )

    if exit_threshold >= entry_threshold:
        raise ValueError(
            "Le seuil de sortie doit être inférieur "
            "au seuil d'entrée."
        )

    target_positions = pd.Series(
        index=zscore.index,
        dtype=float,
        name="target_position",
    )

    # Au début, aucune position n'est ouverte.
    current_position = 0

    for date, current_zscore in zscore.items():

        # Les premières valeurs du z-score sont manquantes,
        # car la fenêtre glissante n'est pas encore complète.
        if pd.isna(current_zscore):
            target_positions.loc[date] = (
                current_position
            )
            continue

        # Aucune position n'est actuellement ouverte.
        if current_position == 0:

            # SPY est relativement bas par rapport à IVV.
            if current_zscore <= -entry_threshold:
                current_position = 1

            # SPY est relativement haut par rapport à IVV.
            elif current_zscore >= entry_threshold:
                current_position = -1

        # Une position longue sur le spread est ouverte.
        elif current_position == 1:

            # Le spread est revenu près de sa moyenne.
            if current_zscore >= -exit_threshold:
                current_position = 0

        # Une position courte sur le spread est ouverte.
        elif current_position == -1:

            # Le spread est revenu près de sa moyenne.
            if current_zscore <= exit_threshold:
                current_position = 0

        target_positions.loc[date] = (
            current_position
        )

    return target_positions.astype(int)