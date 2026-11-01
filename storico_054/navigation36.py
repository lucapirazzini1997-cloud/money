"""Make existing progression interactions visible and their hints specific.

Preserve all story conditions, rewards, trainer scripts and persistent IDs.
"""
from engine32 import *
import visuals33 as V, places32 as A, scr

BASE35 = '9c3ac0a0bc607548f7c2b8f21b8d7ebcdfb2836e854670d317cb245b1786c2d9'


def install():
    assert hashlib.sha256(W.d).hexdigest() == BASE35
    key = (34, 88)
    before = W.rom.map(*key)
    assert [(b['x'], b['y']) for b in before['bgs']] == [(11, 11), (12, 11)]
    panel_script = before['bgs'][0]['arg'] - B
    assert any(n == 'setflag' and a == [0x2a0]
               for _, n, a in scr.decode(W.d, panel_script, 120)[0])
    V.init()
    cv = V.live_canvas(key)
    cv.place_art(10, 10, A.apparatus())
    cv.place_art(10, 9, A.labelart('QUADRO', 4))
    emit(cv, 'rev36_mic_quadro_visibile')
    W.changes.append(dict(name='mic_quadro_visibile', map=key,
                          script=panel_script, coordinates=[[11, 11], [12, 11]],
                          new_flags=[], event_coordinates_preserved=True))

    key = (34, 98)
    before = W.rom.map(*key)
    assert [(b['x'], b['y']) for b in before['bgs']] == [(4, 9)]
    panel_script = before['bgs'][0]['arg'] - B
    assert any(n == 'setflag' and a == [0x2ab]
               for _, n, a in scr.decode(W.d, panel_script, 120)[0])
    cv = V.live_canvas(key)
    cv.place_art(3, 8, A.apparatus())
    cv.place_art(3, 7, A.labelart('QUADRO', 4))
    emit(cv, 'rev36_mausoleo_registratore_visibile')
    W.changes.append(dict(name='mausoleo_registratore_visibile', map=key,
                          script=panel_script, coordinates=[[4, 9]],
                          new_flags=[], event_coordinates_preserved=True))

    # These four branches previously shared the same generic "rilievi" reply.
    # Change only each failure destination; leave the successful reward path intact.
    hints = [
        (0x2d7ecd, 0x86a,
         'DARIO: Per iniziare il corso di canoa serve la quarta medaglia. '
         'Aiuta Lia e Nello a Forli, poi sfida Ivano nella palestra.'),
        (0x2d7ed6, 0x296,
         'DARIO: Marina, al San Domenico di Forli, presenta il corso. '
         "La prima prova e con Luca, qui sull'argine a nord di me."),
        (0x2d7edf, 0x297,
         'DARIO: Hai superato Luca! Ora cerca Sara nella parte centrale '
         "dell'argine, vicino al fiume."),
        (0x2d7ee8, 0x298,
         "DARIO: Manca l'ultima prova: Diego ti aspetta a nord-est "
         "dell'argine. Dopo la vittoria torna da me per Surf."),
    ]
    branches = []
    for at, prerequisite, text in hints:
        assert W.d[at:at + 2] == b'\x06\x00'
        assert struct.unpack_from('<I', W.d, at + 2)[0] == B + 0x2d7939
        p = Script('Dario indizio ' + hex(prerequisite)).msg(text).end().save()
        struct.pack_into('<I', W.d, at + 2, B + p)
        branches.append(dict(address=at, prerequisite=prerequisite, script=p))
    W.changes.append(dict(name='dario_prossima_prova', map=[34, 84],
                          branches=branches, reward_script_preserved=True))

    # The adventure is already implemented beyond Faenza; remove the obsolete
    # "next chapter" message without inventing a direct northern connection.
    key = (34, 85)
    objects = copy.deepcopy(W.rom.map(*key)['objects'])
    o = next(o for o in objects if o['id'] == 7)
    previous = o['script']
    s = Script('Faenza indicazioni Ravenna').emit(b'\x6a\x5a').flag(0x86b, 'ravenna')
    s.msg('Prima di ripartire, aiuta il MIC e conquista la medaglia di Ada. '
          'Al Podesta, a nord della piazza, Alma ti spiega come iniziare.').end()
    s.label('ravenna').msg('Ravenna si raggiunge dalla pineta a nord di Lido di Savio. '
                         'Puoi tornare verso Forli attraverso il fiume usando Surf. '
                         'A Ravenna cerca Camilla negli archivi.').end()
    o['script'] = s.save()
    events(key, objects=objects)
    W.changes.append(dict(name='faenza_indicazioni_capitolo_successivo', map=key,
                          local_id=7, previous_script=previous, script=o['script']))
