import asyncio
from notionary import NotionPage


async def multiple_toggler_integrations():
    url = "https://www.notion.so/Jarvis-Clipboard-1a3389d57bd380d7a507e67d1b25822c"
    page_manager = NotionPage(url=url)

    example_output = """!> [📚] AI Summary: Explore the fascinating connection between the nervous system and muscle movement. Discover the differences between training for hypertrophy and strength, alongside effective resistance protocols. Learn how to assess recovery with tools like heart rate variability and grip strength. Dive into the impact of key nutrients such as creatine and electrolytes on muscle performance. This discussion offers actionable strategies to enhance movement, preserve strength with age, and boost energy levels.

+++ 🎧 Audio Summary
    $[AI-generated audio summary](https://storage.googleapis.com/audio_summaries/ep_ai_summary_127d02ec-ca12-4312-a5ed-cb14b185480c.mp3)

<!-- spacer -->

## ⬆️ Key Insights
- The interplay between the nervous system and muscle fibers is critical for effective muscle contraction and movement coordination.
- Adequate nutrition, particularly protein and electrolytes, coupled with proper recovery practices, is essential for optimizing muscle growth and performance.
- Regular strength training helps offset age-related muscle decline and improves overall posture and functional movement.
- Simple tools like grip strength measurements and heart rate variability can provide valuable insights into recovery status and training readiness.

<!-- spacer -->
---

### 💪 1. Understanding Muscle Strength
- Muscles naturally weaken with age; strength training helps offset this decline and improve posture and movement.
- The *Henneman size principle* explains how our bodies efficiently recruit muscle fibers based on the weight of an object, prioritizing energy conservation.
- Neural adaptations are the primary driver of strength gains in the initial weeks of training, before hypertrophy becomes significant.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/a1b2c3d4)
    ... "When we talk about strength training, we're primarily focusing on the neurological adaptations that occur first. What's fascinating is that during the first 4-6 weeks of a strength program, most of your strength gains come from improved neural efficiency, not muscle size. Your brain is literally learning to recruit more muscle fibers simultaneously, creating greater force output with the same muscle mass."


### 🧠 2. The Nervous System's Role
- The central nervous system coordinates which motor units are activated and in what sequence when performing movements.
- *Motor unit recruitment* follows a specific pattern that prioritizes smaller, more precise units before larger, more powerful ones.
- Fatigue can significantly impact nervous system efficiency, reducing both strength output and movement quality.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/e5f6g7h8)
    ... "The beauty of how our nervous system works is that it's incredibly adaptive. When you're learning a new movement, your brain is creating new neural pathways. With practice, these pathways become more efficient—similar to how a path through grass becomes more defined the more it's walked on. This is why technique practice is so crucial; you're literally building the neural infrastructure for efficient movement."


### 🔬 3. Assessing Recovery Through Simple Tests
- *Heart rate variability* (HRV) is a key indicator of recovery, but can be difficult to measure accurately without specialized equipment.
- Morning grip strength is a simple, readily available test to assess whole-system recovery and inform training decisions.
- Sleep quality has a direct correlation with both HRV and grip strength measurements.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/i9j0k1l2)
    ... "One of the simplest recovery tools you have access to is grip strength. First thing in the morning, try squeezing a hand dynamometer or even just observe how your grip feels. If it's significantly weaker than your baseline, that's often an indicator your nervous system is still fatigued. This simple test has been shown to correlate with overall systemic recovery and can help you decide whether to push hard in training or take a lighter approach that day."


### 🥗 4. Nutrition for Muscle Performance
- *Creatine monohydrate* remains one of the most well-researched and effective supplements for improving strength and power output.
- Adequate *electrolyte balance* is critical for optimal muscle contraction and preventing cramping during exercise.
- Protein timing and distribution throughout the day may be as important as total daily intake for maximizing muscle protein synthesis.
+++ Transcript
    <embed:Listen to this highlight>(https://snipd.com/snip/m3n4o5p6)
    ... "The research on creatine is remarkably consistent. A dose of 3-5 grams daily increases phosphocreatine stores in your muscles, enhancing your capacity for high-intensity, short-duration activities. What's often overlooked is how it can benefit cognitive function as well. Your brain uses a significant amount of ATP, and creatine supports that energy production. This is why some studies show improvements in cognitive tasks, particularly under sleep-deprived conditions, when supplementing with creatine."
"""

    await page_manager.append_markdown(markdown=example_output)

    page_content = await page_manager.get_text()

    print("Page Content:")
    print(page_content)


async def long_text_demo():
    url = "https://www.notion.so/Jarvis-Clipboard-1a3389d57bd380d7a507e67d1b25822c"
    page_manager = NotionPage(url=url)

    markdown_text = """
Die künstliche Intelligenz steht an einem Wendepunkt ihrer Entwicklung, an dem sie nicht mehr nur als technologisches Werkzeug betrachtet wird, sondern zunehmend als Partner in kreativen und intellektuellen Prozessen. Diese Transformation ist das Ergebnis jahrzehntelanger Forschung und Entwicklung, die von den frühen symbolischen KI-Systemen der 1950er und 1960er Jahre über die Expertensysteme der 1980er Jahre bis hin zu den heutigen tiefen neuronalen Netzwerken und Transformer-Modellen reicht. Der aktuelle Durchbruch in der KI, insbesondere im Bereich des maschinellen Lernens und des Natural Language Processing, beruht auf mehreren Schlüsselfaktoren: der Verfügbarkeit enormer Datenmengen zum Training dieser Modelle, der exponentiellen Steigerung der Rechenleistung, die es ermöglicht, komplexere Modelle zu trainieren, und den Fortschritten bei den Algorithmen selbst, insbesondere bei den Architekturen neuronaler Netzwerke. Diese Konvergenz hat zu KI-Systemen geführt, die in der Lage sind, menschliche Sprache mit beispielloser Genauigkeit zu verstehen und zu generieren, Bilder zu analysieren und zu erstellen und sogar Musik zu komponieren, die von menschlichen Kompositionen kaum zu unterscheiden ist. Während diese Fortschritte zahlreiche positive Anwendungen ermöglichen, von personalisierten Bildungserfahrungen bis hin zu effizienteren Gesundheitssystemen, werfen sie auch wichtige ethische Fragen auf, die unsere Gesellschaft angehen muss. Dazu gehören Bedenken hinsichtlich der Privatsphäre, da KI-Systeme oft mit großen Mengen persönlicher Daten trainiert werden, Fragen der Transparenz und Erklärbarkeit, da viele fortschrittliche KI-Modelle als "Black Boxes" fungieren, deren Entscheidungsprozesse schwer zu verstehen sind, und Bedenken hinsichtlich möglicher Verzerrungen und Diskriminierungen, die in diese Systeme eingebaut sein könnten. Darüber hinaus gibt es Fragen zur Zukunft der Arbeit, da KI-Systeme immer mehr Aufgaben übernehmen können, die traditionell von Menschen ausgeführt wurden. Es ist daher entscheidend, dass wir als Gesellschaft einen aktiven Dialog darüber führen, wie wir diese Technologien entwickeln und einsetzen wollen, um sicherzustellen, dass sie zum Wohle aller eingesetzt werden. Dies erfordert nicht nur technisches Fachwissen, sondern auch Beiträge aus Bereichen wie Ethik, Soziologie, Philosophie und Recht. Nur durch einen solchen interdisziplinären Ansatz können wir das volle Potenzial der künstlichen Intelligenz ausschöpfen und gleichzeitig sicherstellen, dass sie im Einklang mit unseren Werten und Zielen als Gesellschaft steht. In den kommenden Jahren werden wir wahrscheinlich Zeugen weiterer bedeutender Fortschritte auf dem Gebiet der künstlichen Intelligenz sein. Insbesondere könnten wir Fortschritte in Richtung einer allgemeineren KI sehen, die sich über einzelne, eng definierte Aufgaben hinaus entwickelt und in der Lage ist, Wissen und Fähigkeiten über verschiedene Domänen hinweg zu übertragen, ähnlich wie es Menschen tun. Dies könnte zu KI-Systemen führen, die nicht nur darauf trainiert sind, bestimmte Aufgaben zu erfüllen, sondern die in der Lage sind, zu lernen, zu schlussfolgern und sich an neue Situationen anzupassen, was ein höheres Maß an Autonomie und Kreativität ermöglicht. Gleichzeitig könnte es zu Fortschritten bei der Integration von KI in andere aufkommende Technologien kommen, wie z. B. das Internet der Dinge, die virtuelle und erweiterte Realität und die Robotik, was zu neuen Formen der Mensch-Computer-Interaktion und neuen Anwendungen in Bereichen wie dem Gesundheitswesen, der Bildung und der Unterhaltung führen könnte. Es ist jedoch wichtig zu beachten, dass die Entwicklung der KI nicht vorherbestimmt ist, sondern durch die Entscheidungen geprägt wird, die wir als Gesellschaft treffen, einschließlich der Frage, welche Forschungsbereiche wir priorisieren, wie wir KI regulieren und wie wir sie in verschiedene Aspekte unseres Lebens integrieren. Daher ist es wichtig, dass wir weiterhin einen offenen und integrativen Dialog über die Zukunft der KI führen und sicherstellen, dass ihre Entwicklung und ihr Einsatz im Einklang mit unseren gemeinsamen Werten und Zielen stehen. Die Auseinandersetzung mit technologischen Fragen führt unweigerlich zu tiefen philosophischen Überlegungen. Was bedeutet es, intelligent zu sein? Was unterscheidet menschliches Denken von maschinellem Denken? Wird es jemals möglich sein, das menschliche Bewusstsein vollständig zu verstehen und zu replizieren? Während die KI-Forschung voranschreitet, stößt sie an die Grenzen unseres Verständnisses von Intelligenz, Bewusstsein und Identität und wirft Fragen auf, mit denen sich Philosophen seit Jahrhunderten auseinandersetzen. Dieses Zusammenspiel von Technologie und Philosophie kann zu neuen Erkenntnissen über die Natur des Geistes und des Selbst führen. Zugleich ergeben sich neue Fragen, etwa ob Maschinen jemals ein Bewusstsein oder subjektive Erfahrungen haben könnten, wie wir sie kennen, und welche ethischen Implikationen dies haben könnte. Würden wir Maschinen mit Bewusstsein den gleichen moralischen Status und die gleichen Rechte zugestehen wie Menschen oder anderen empfindungsfähigen Wesen? Während wir noch weit davon entfernt sind, Maschinen mit echtem Bewusstsein zu erschaffen, werden diese Fragen mit dem Fortschritt der Technologie immer relevanter. Es ist wichtig, dass wir sie jetzt angehen, damit wir auf zukünftige Entwicklungen vorbereitet sind. Neben diesen philosophischen Fragen wirft der Fortschritt der KI auch praktische ethische Fragen auf, wie z. B. die Frage der Verantwortlichkeit. Wenn KI-Systeme immer autonomer werden und Entscheidungen treffen, die erhebliche Auswirkungen auf das menschliche Leben haben können, wie z. B. im Gesundheitswesen, im Finanzwesen oder im Straßenverkehr, wer ist dann verantwortlich, wenn etwas schief geht? Ist es der Entwickler des KI-Systems, der Benutzer oder das System selbst? Diese Fragen der Verantwortlichkeit werden immer komplexer, da KI-Systeme immer autonomer und undurchsichtiger werden. Gleichzeitig stellt sich die Frage der Kontrolle und Regulierung. Da KI-Systeme immer leistungsfähiger werden, steigen auch die potenziellen Risiken eines Missbrauchs oder eines unkontrollierten Einsatzes. Wie können wir sicherstellen, dass diese Systeme in einer Weise entwickelt und eingesetzt werden, die im Einklang mit den menschlichen Werten und dem Gemeinwohl steht? Welche Art von Regulierung oder Aufsicht ist erforderlich? Diese Fragen sind nicht nur technischer Natur, sondern betreffen auch grundlegende gesellschaftliche und politische Fragen darüber, wie wir Technologie steuern und wie wir sicherstellen, dass sie dem Gemeinwohl dient. Schließlich gibt es die Frage der globalen Zusammenarbeit und des Wettbewerbs. Da die KI zu einer immer wichtigeren Technologie wird, die erhebliche wirtschaftliche und strategische Vorteile bieten kann, besteht die Gefahr eines "KI-Rennens" zwischen Nationen oder Unternehmen, das auf Kosten der Sicherheit, Ethik oder gemeinsamen internationalen Standards gehen könnte. Die Geschichte hat gezeigt, dass technologische Revolutionen sowohl Chancen als auch Risiken mit sich bringen können, und die Art und Weise, wie wir mit ihnen umgehen, kann den Unterschied zwischen einer utopischen und einer dystopischen Zukunft ausmachen. Es ist daher wichtig, dass wir globale Dialoge und Zusammenarbeit fördern, um sicherzustellen, dass die Entwicklung und der Einsatz von KI zum Nutzen aller und im Einklang mit den gemeinsamen Werten und Zielen der Menschheit stattfinden. Die KI wirft somit ein breites Spektrum an Fragen auf, von technischen und philosophischen bis hin zu ethischen, gesellschaftlichen und politischen. Die Art und Weise, wie wir mit diesen Fragen umgehen, wird die Zukunft der KI und damit auch die Zukunft unserer Gesellschaft prägen. Es liegt an uns allen - Forschern, Entwicklern, politischen Entscheidungsträgern, Wirtschaftsführern und Bürgern -, aktiv an diesem Diskurs teilzunehmen und sicherzustellen, dass die Entwicklung und der Einsatz von KI im Einklang mit unseren Werten und Zielen als Menschheit stehen.
"""
    await page_manager.append_markdown(markdown=markdown_text)


if __name__ == "__main__":
    asyncio.run(multiple_toggler_integrations())
    print("\nDemonstration completed.")
