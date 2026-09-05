"""
srs.py
Implementacao do algoritmo SM-2 de repeticao espacada
(o mesmo algoritmo em que o Anki se baseia), com um passo curto de
"De novo" em minutos, igual ao Anki faz antes de virar um intervalo
de dias.

O usuario avalia cada card apos ver a resposta, com uma nota de 0 a 5:
    0-2 -> "De novo"  -> errou, reaparece em poucos minutos
    3   -> "Dificil" -> avanca pouco
    4   -> "Bom"      -> avanca normalmente
    5   -> "Facil"    -> avanca mais e aumenta o fator de facilidade
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

MIN_EASE_FACTOR = 1.3

# Quantos minutos o card demora para voltar quando o usuario clica em "De novo"
AGAIN_STEP_MINUTES = 10


@dataclass
class ReviewResult:
    ease_factor: float
    interval_days: float  # pode ser fracionario quando for um passo de minutos
    repetitions: int
    due_date: str  # data e hora em ISO 8601


def review_card(quality: int, ease_factor: float, interval_days: float,
                 repetitions: int, now: datetime = None) -> ReviewResult:
    """
    Calcula o novo estado de um card apos uma revisao.

    quality: nota de 0 a 5 dada pelo usuario.
    ease_factor: fator de facilidade atual do card (comeca em 2.5).
    interval_days: intervalo atual em dias (pode ser fracionario).
    repetitions: quantas vezes o card foi respondido corretamente em sequencia.
    now: horario de referencia (usado apenas em testes; padrao = agora).
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality deve estar entre 0 e 5")

    now = now or datetime.now()

    if quality < 3:
        # Errou: reinicia a contagem de repeticoes e volta a aparecer
        # em poucos minutos, ainda na mesma sessao de estudo.
        repetitions = 0
        interval_days = AGAIN_STEP_MINUTES / (24 * 60)
        due = now + timedelta(minutes=AGAIN_STEP_MINUTES)
    else:
        if repetitions == 0:
            base = 1
        elif repetitions == 1:
            base = 6
        else:
            base = interval_days * ease_factor

        # Cada nota avanca o intervalo de um jeito diferente, assim como
        # no Anki: "Dificil" cresce pouco, "Bom" segue o fator de
        # facilidade normal, "Facil" ganha um bonus extra.
        if quality == 3:
            interval_days = max(1, round(base * 0.8))
        elif quality == 4:
            interval_days = max(1, round(base))
        else:  # quality == 5
            interval_days = max(1, round(base * 1.3))

        repetitions += 1
        due = now + timedelta(days=interval_days)

    # Atualiza o fator de facilidade (formula padrao do SM-2)
    ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ease_factor < MIN_EASE_FACTOR:
        ease_factor = MIN_EASE_FACTOR

    return ReviewResult(
        ease_factor=round(ease_factor, 3),
        interval_days=interval_days,
        repetitions=repetitions,
        due_date=due.isoformat(),
    )


def format_interval(interval_days: float) -> str:
    """
    Formata um intervalo (em dias, podendo ser fracionario) como texto
    curto para mostrar nos botoes de revisao. Ex: '<10min', '4dia(s)',
    '15dia(s)', '1,1mes(es)'.
    """
    minutes = interval_days * 24 * 60

    if minutes < 60:
        m = max(1, round(minutes))
        return f"<{m}min"

    hours = minutes / 60
    if hours < 24:
        return f"{round(hours)}h"

    days = interval_days
    if days < 30:
        d = round(days)
        return f"{d}dia(s)"

    months = days / 30
    if months < 12:
        return f"{months:.1f}".replace(".", ",") + "mes(es)"

    years = days / 365
    return f"{years:.1f}".replace(".", ",") + "ano(s)"


def preview_intervals(ease_factor: float, interval_days: float, repetitions: int) -> dict:
    """
    Calcula, sem salvar nada, qual seria o texto de intervalo mostrado
    em cada botao (De novo=1, Dificil=3, Bom=4, Facil=5), a partir do
    estado atual do card. Usado para exibir a previsao nos botoes antes
    do usuario clicar.
    """
    previews = {}
    for quality in (1, 3, 4, 5):
        result = review_card(quality, ease_factor, interval_days, repetitions)
        previews[quality] = format_interval(result.interval_days)
    return previews
