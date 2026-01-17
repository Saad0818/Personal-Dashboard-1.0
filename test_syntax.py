
accent_primary = "blue"
accent_secondary = "red"
days = 5

ms = type('obj', (object,), {'title':'foo', 'due_date': 'bar'})

card_html = (
    f"""<div style="background: linear-gradient(135deg, #111827 0%, #4B5563 100%); border-radius:24px; padding:2.5rem 2rem; position: relative; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);">"""
    f"""    <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(79, 70, 229, 0.15) 0%, rgba(0,0,0,0) 50%);"></div>"""
    f"""    <div style="position: relative; z-index: 1;">"""
    f"""            <div style="font-size:0.85rem; font-weight:700; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.5rem;">Next Milestone</div>"""
    f"""            <div style="font-size:3.5rem; font-weight:800; color:#FFFFFF; line-height:1; letter-spacing:-0.03em;">"""
    f"""            {days}<span style="font-size:1rem; font-weight:600; color:#9CA3AF; margin-left:8px; vertical-align:middle;">DAYS REMAINING</span>"""
    f"""        </div>"""
    f"""            <div style="margin: 1.5rem 0; height: 6px; width: 100%; background: rgba(255,255,255,0.1); border-radius: 100px; overflow:hidden;">"""
    f"""            <div style="height: 100%; width: {max(0, min(100, 100 - (days*5)))}%; background: linear-gradient(90deg, {accent_primary}, {accent_secondary}); border-radius: 100px;"></div>"""
    f"""        </div>"""
    f"""        <div style="font-size:1.5rem; font-weight:700; color:#FFFFFF; line-height:1.3;">"""
    f"""            "{ms.title}" """
    f"""        </div>"""
    f"""            <div style="margin-top:1.5rem; display:inline-flex; align-items:center; gap:8px; padding: 8px 16px; background:rgba(255,255,255,0.05); border-radius:100px; border:1px solid rgba(255,255,255,0.1);">"""
    f"""            <span style="color:{accent_secondary}">\U0001F3AF</span>"""
    f"""            <span style="font-size:0.85rem; font-weight:500; color:#E5E7EB;">Target: {ms.due_date}</span>"""
    f"""        </div>"""
    f"""    </div>"""
    f"""</div>"""
)
print("Syntax OK")
