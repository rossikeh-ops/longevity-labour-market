"""
Reusable interactive choropleth section for the HTML reports.

build_map_section(data, container, default_metric, title, intro) returns a string
of HTML+CSS+JS with the data INLINED (no fetch — so it works when the report is
opened as a local file://). D3 + TopoJSON load from CDN. All CSS classes are
prefixed `gm-` and scoped to the container id so they don't clash with report CSS.

`data` schema (same as outputs/map_data.json):
  {countries:{ISO:Name}, regime:{ISO:str},
   metrics:{key:{label,unit,fmt('millions'|'plain'),values:{ISO:{F,M,T}},years:{ISO:int}}}}
"""
from __future__ import annotations
import json


def build_map_section(data: dict, *, container: str = "geomap",
                      default_metric: str | None = None,
                      title: str = "Geographic overview",
                      intro: str = "") -> str:
    default = default_metric or next(iter(data["metrics"]))
    payload = json.dumps({"data": data, "container": container, "default": default})
    cid = container
    css = f"""
#{cid} .gm-wrap{{display:flex;gap:16px;flex-wrap:wrap;align-items:stretch}}
#{cid} .gm-map{{background:var(--card,#FFFFFF);border:1px solid var(--line,#E7E5E4);
  border-radius:12px;padding:8px;flex:1 1 560px;min-width:320px;position:relative}}
#{cid} .gm-side{{flex:0 0 250px;display:flex;flex-direction:column;gap:12px}}
#{cid} .gm-ctl{{background:var(--card,#FFFFFF);border:1px solid var(--line,#E7E5E4);
  border-radius:12px;padding:14px}}
#{cid} .gm-lab{{display:block;font-size:11px;color:var(--mut,#78716C);margin:0 0 6px;
  text-transform:uppercase;letter-spacing:.6px}}
#{cid} select{{width:100%;background:#F5F5F4;color:var(--ink,#292524);
  border:1px solid var(--line,#E7E5E4);border-radius:8px;padding:8px 9px;font-size:14px}}
#{cid} .gm-seg{{display:flex;gap:5px;margin-top:4px}}
#{cid} .gm-seg button{{flex:1;background:#F5F5F4;color:var(--mut,#78716C);
  border:1px solid var(--line,#E7E5E4);border-radius:8px;padding:7px 0;font-size:13px;cursor:pointer}}
#{cid} .gm-seg button.on{{background:var(--acc,#166534);color:#FFFFFF;
  border-color:var(--acc,#166534);font-weight:600}}
#{cid} .gm-scale{{display:flex;align-items:center;gap:8px;margin-top:10px;font-size:11px;color:var(--mut,#78716C)}}
#{cid} .gm-bar{{height:11px;flex:1;border-radius:3px}}
#{cid} .gm-meta{{font-size:11px;color:var(--mut,#78716C);margin-top:8px}}
#{cid} .gm-rank{{background:var(--card,#FFFFFF);border:1px solid var(--line,#E7E5E4);
  border-radius:12px;padding:12px 14px}}
#{cid} .gm-rank h4{{margin:0 0 9px;font-size:11px;color:var(--mut,#78716C);
  font-weight:600;text-transform:uppercase;letter-spacing:.6px}}
#{cid} .gm-row{{display:flex;align-items:center;gap:7px;margin:4px 0;font-size:12px}}
#{cid} .gm-row .nm{{width:74px;color:var(--ink,#292524)}}
#{cid} .gm-row .tk{{height:13px;border-radius:3px;min-width:2px}}
#{cid} .gm-row .vl{{color:var(--mut,#78716C);font-variant-numeric:tabular-nums}}
#{cid} .gm-c{{stroke:#FFFFFF;stroke-width:.6px;cursor:pointer}}
#{cid} .gm-c.other{{fill:#E7E5E4;stroke:#E7E5E4}}
#{cid} .gm-c:hover{{opacity:.82}}
#{cid} .gm-clab{{font-size:10px;fill:#292524;font-weight:700;pointer-events:none;text-anchor:middle;
  paint-order:stroke;stroke:#FFFFFF;stroke-width:2.5px;stroke-linejoin:round}}
#{cid} .gm-tip{{position:absolute;pointer-events:none;background:#FFFFFF;
  border:1px solid var(--acc,#166534);border-radius:8px;padding:8px 11px;font-size:12px;
  color:var(--ink,#292524);opacity:0;max-width:210px;box-shadow:0 6px 20px rgba(0,0,0,.4)}}
#{cid} .gm-tip b{{color:var(--acc,#166534)}}
"""
    intro_html = f'<p class="sub">{intro}</p>' if intro else ""
    body = f"""<h2>{title}</h2>{intro_html}
<div id="{cid}"><style>{css}</style>
<div class="gm-wrap">
  <div class="gm-map"><svg class="gm-svg" viewBox="0 0 720 520" width="100%" style="display:block"></svg>
    <div class="gm-tip"></div></div>
  <div class="gm-side">
    <div class="gm-ctl">
      <label class="gm-lab">Metric</label><select class="gm-metric"></select>
      <label class="gm-lab" style="margin-top:12px">Sex</label>
      <div class="gm-seg"><button data-s="T" class="on">Total</button>
        <button data-s="F">Women</button><button data-s="M">Men</button></div>
      <div class="gm-scale"><span class="gm-lo"></span><div class="gm-bar"></div><span class="gm-hi"></span></div>
      <div class="gm-meta"></div>
    </div>
    <div class="gm-rank"><h4>Ranking</h4><div class="gm-list"></div></div>
  </div>
</div></div>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
<script>(function(){{
const CFG={payload};
const ISO={{Bulgaria:"BG",Poland:"PL",Czechia:"CZ","Czech Republic":"CZ",Romania:"RO",
  Germany:"DE",France:"FR",Norway:"NO",Switzerland:"CH"}};
const DATA=CFG.data, root=document.getElementById(CFG.container);
let state={{metric:CFG.default, sex:"T"}};
const $=s=>root.querySelector(s);
function fmt(v,f){{ if(v==null||isNaN(v))return"n/a";
  if(f==="millions"){{ const a=Math.abs(v),s=v<0?"-":"";
    if(a>=1e9)return s+(a/1e9).toFixed(2)+" bn"; if(a>=1e6)return s+(a/1e6).toFixed(2)+" M";
    return d3.format(",")(Math.round(v)); }} return d3.format(",.2~f")(v); }}
fetch("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json").then(r=>r.json()).then(topo=>{{
  const sel=d3.select($(".gm-metric"));
  Object.entries(DATA.metrics).forEach(([k,m])=>sel.append("option").attr("value",k).text(m.label));
  sel.property("value",state.metric);
  const feats=topojson.feature(topo,topo.objects.countries).features;
  // keep only European polygons (drops France's overseas territories, Svalbard…)
  const euroOnly=f=>{{ if(f.geometry.type!=="MultiPolygon") return f;
    const polys=f.geometry.coordinates.filter(poly=>{{
      const c=d3.geoCentroid({{type:"Polygon",coordinates:poly}});
      return c[0]>-25&&c[0]<45&&c[1]>34&&c[1]<73;}});
    return {{...f,geometry:{{type:"MultiPolygon",coordinates:polys.length?polys:f.geometry.coordinates}}}};}};
  const eight=feats.filter(f=>Object.keys(DATA.countries).includes(ISO[f.properties.name])).map(euroOnly);
  const svg=d3.select($(".gm-svg"));
  const proj=d3.geoConicConformal().rotate([-10,0]).parallels([43,62])
    .fitExtent([[28,20],[692,470]],{{type:"FeatureCollection",features:eight}});
  const path=d3.geoPath(proj);
  const inEU=f=>{{try{{const[[w,s],[e,n]]=d3.geoBounds(f);
    return n>33&&s<73&&w<55&&e>-32&&(e-w)<90;}}catch(_){{return false;}}}};
  svg.append("g").selectAll("path").data(feats.filter(inEU)).join("path").attr("class","gm-c other").attr("d",path);
  const g=svg.append("g");
  g.selectAll("path").data(eight).join("path").attr("class","gm-c")
    .attr("data-iso",d=>ISO[d.properties.name]).attr("d",path)
    .on("mousemove",hover).on("mouseleave",()=>d3.select($(".gm-tip")).style("opacity",0));
  svg.append("g").selectAll("text").data(eight).join("text").attr("class","gm-clab")
    .attr("x",d=>path.centroid(d)[0]).attr("y",d=>path.centroid(d)[1]+3).text(d=>ISO[d.properties.name]);
  sel.on("change",function(){{state.metric=this.value;render();}});
  d3.selectAll(root.querySelectorAll(".gm-seg button")).on("click",function(){{
    root.querySelectorAll(".gm-seg button").forEach(b=>b.classList.remove("on"));
    this.classList.add("on");state.sex=this.dataset.s;render();}});
  function vlist(){{const m=DATA.metrics[state.metric];
    return Object.keys(DATA.countries).map(iso=>({{iso,v:(m.values[iso]||{{}})[state.sex]??null}}));}}
  function render(){{
    const m=DATA.metrics[state.metric];
    const arr=vlist().filter(d=>d.v!=null).map(d=>d.v),lo=d3.min(arr),hi=d3.max(arr);
    // diverging metrics (e.g. the balance: surplus vs shortage) use a red→green
    // scale centred on zero; everything else a sequential YlGnBu scale.
    const div=!!m.diverging, PAL=div?d3.interpolateRgbBasis(["#B91C1C","#FEF3C7","#166534"]):d3.interpolateRgbBasis(["#FEF3C7","#4ADE80","#166534"]);
    const mag=Math.max(Math.abs(lo),Math.abs(hi))||1;
    const seq=d3.scaleSequential(PAL).domain([lo,hi]);
    const color=v=>div?PAL(0.5+0.5*v/mag):seq(v);
    g.selectAll("path.gm-c")
      .attr("fill",d=>{{const v=(m.values[ISO[d.properties.name]]||{{}})[state.sex];return v==null?"#E7E5E4":color(v);}});
    $(".gm-bar").style.background=`linear-gradient(90deg,${{d3.range(0,1.01,.1).map(t=>PAL(t)).join(",")}})`;
    $(".gm-lo").textContent=fmt(lo,m.fmt);$(".gm-hi").textContent=fmt(hi,m.fmt);
    const yrs=Object.values(m.years||{{}});
    $(".gm-meta").innerHTML=`Unit: <b style="color:var(--ink,#292524)">${{m.unit}}</b> · years ${{d3.min(yrs)}}–${{d3.max(yrs)}}`;
    const sorted=vlist().filter(d=>d.v!=null).sort((a,b)=>b.v-a.v);
    const maxw=div?mag:(hi||1);
    const bw=d3.scaleLinear().domain([0,maxw]).range([0,140]);
    const list=d3.select($(".gm-list")).html("");
    sorted.forEach(d=>{{const row=list.append("div").attr("class","gm-row");
      row.append("span").attr("class","nm").text(DATA.countries[d.iso]);
      row.append("span").attr("class","tk").style("width",bw(Math.abs(d.v))+"px").style("background",color(d.v));
      row.append("span").attr("class","vl").text(fmt(d.v,m.fmt));}});
  }}
  function hover(ev,d){{const iso=ISO[d.properties.name],m=DATA.metrics[state.metric],rec=m.values[iso]||{{}};
    const tip=d3.select($(".gm-tip"));
    const rows=["T","F","M"].filter(s=>rec[s]!=null)
      .map(s=>`${{({{T:"Total",F:"Women",M:"Men"}})[s]}}: <b>${{fmt(rec[s],m.fmt)}}</b>`).join("<br>");
    tip.html(`<b>${{DATA.countries[iso]}}</b> · ${{DATA.regime[iso]}}<br>
      <span style="color:var(--mut,#78716C)">${{m.label}}</span><br>${{rows||"n/a"}}`).style("opacity",1);
    const r=$(".gm-svg").getBoundingClientRect(),mr=$(".gm-map").getBoundingClientRect();
    tip.style("left",(ev.clientX-mr.left+14)+"px").style("top",(ev.clientY-mr.top+10)+"px");}}
  render();
}});
}})();</script>"""
    return body
