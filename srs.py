"""
srs.py
Implementacao do algoritmo SM-2 de repeticao espacada
(o mesmo algoritmo em que o Anki se baseia).

O usuario avalia cada card apos ver a resposta, com uma nota de 0 a 5:
    0-2 -> "Errei" / dificil demais -> reinicia o intervalo
    3   -> "Dificil" -> avanca pouco
    4   -> "Bom"      -> avanca normalmente
    5   -> "Facil"    -> avanca mais e aumenta o fator de facilidade
"""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class ReviewResult:
    ease_factor: float
    interval_days: int
    repetitions: int
    due_date: str  # ISO format


MIN_EASE_FACTOR = 1.3


def review_card(quality: int, ease_factor: float, interval_days: int,
                 repetitions: int) -> ReviewResult:
    """
    Calcula o novo estado de um card apos uma revisao.

    quality: nota de 0 a 5 dada pelo usuario.
    ease_factor: fator de facilidade atual do card (comeca em 2.5).
    interval_days: intervalo atual em dias.
    repetitions: quantas vezes o card foi respondido corretamente em sequencia.
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality deve estar entre 0 e 5")

    if quality < 3:
        # Errou: reinicia a contagem de repeticoes e volta a revisar logo
        repetitions = 0
        interval_days = 1
    else:
        if repetitions == 0:
            interval_days = 1
        elif repetitions == 1:
            interval_days = 6
        else:
            interval_days = round(interval_days * ease_factor)
        repetitions += 1

    # Atualiza o fator de facilidade (formula padrao do SM-2)
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < MIN_EASE_FACTOR:
        ease_factor = MIN_EASE_FACTOR

    due_date = (date.today() + timedelta(days=interval_days)).isoformat()

    return ReviewResult(
        ease_factor=round(ease_factor, 3),
        interval_days=interval_days,
        repetitions=repetitions,
        due_date=due_date,
    )
