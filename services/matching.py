def calculer_score(profil_a, profil_b):
    score = 0
    # Compétences de A couvrant les lacunes de B
    competences_a = set(profil_a.competences or [])
    lacunes_b = set(profil_b.lacunes or [])
    score += len(competences_a.intersection(lacunes_b)) * 20

    # Même filière
    if profil_a.filiere == profil_b.filiere:
        score += 15

    # Niveau proche (simplifié)
    try:
        niv_a = int(''.join(filter(str.isdigit, profil_a.niveau or '')))
        niv_b = int(''.join(filter(str.isdigit, profil_b.niveau or '')))
        ecart = abs(niv_a - niv_b)
        if ecart <= 1:
            score += 10
    except:
        pass

    # Créneaux de disponibilité communs
    dispo_a = { (d['jour'], d['debut'], d['fin']) for d in (profil_a.disponibilites or []) }
    dispo_b = { (d['jour'], d['debut'], d['fin']) for d in (profil_b.disponibilites or []) }
    score += len(dispo_a & dispo_b) * 5

    return score

