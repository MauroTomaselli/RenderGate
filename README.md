# RenderGate - Blender Render Preset Manager 🚀

**RenderGate** è un add-on per Blender scritto in Python progettato per esportare, importare e gestire l'intera configurazione di rendering di una scena Blender attraverso file di testo con estensione `.RGE`.

---

## 🌟 Caratteristiche Principali

1. **Formato `.RGE` Umano e Auto-Documentato**:
   - I file `.RGE` sono basati su JSON formattato con indentazione e codifica UTF-8.
   - Ogni impostazione riporta esplicitamente:
     - `field`: il percorso Python completo (es. `scene.cycles.samples`, `scene.render.resolution_x`)
     - `label`: il nome leggibile dell'impostazione nell'interfaccia di Blender
     - `description`: la descrizione e lo scopo del parametro
     - `type`: tipo di dato (`INT`, `FLOAT`, `BOOLEAN`, `ENUM`, `STRING`)
     - `value`: il valore assegnato
   - Include un blocco metadati con data, versione di Blender con cui è stato generato e note.

2. **Compatibilità Cross-Version (es. Blender 4.x ↔ Blender 5.x)**:
   - Se carichi un preset creato con una versione diversa di Blender (es. esportato da Blender 4.5 e importato in Blender 5.2):
     - Tutte le impostazioni compatibili vengono applicate regolarmente.
     - Qualsiasi proprietà rimossa, rinominata o deprecata (es. il Bloom legacy di EEVEE sostituito in Blender 4.2+ da EEVEE Next, o nuovi color space AgX / ACES) viene rilevata e gestita senza bloccare il rendering.
     - Viene generato un **Report di Compatibilità** dettagliato con il motivo esatto del mancato assegnamento e suggerimenti di migrazione.

3. **Integrazione con il Sistema Standard di Blender**:
   - **Pannello Proprietà**: situato direttamente in `Properties > Render > RenderGate Presets`.
   - **Libreria Preset**: salvataggio rapido con il pulsante `+` e cancellazione con `-` nella directory standard dei preset utente (`presets/rendergate`).
   - **File Browser di Blender**:
     - `File > Export > RenderGate Preset (.RGE)`
     - `File > Import > RenderGate Preset (.RGE)`
     - Filtri per categoria (Dimensioni, Motore, Gestione Colore, Cycles, EEVEE, Output, Pass di Render).

4. **Preset Inclusi Out-of-the-Box**:
   - `Cycles_Production_4K_AgX.RGE`: Configurazione Cycles in 4K ad alta campionatura (Denoising OIDN, 4096 campioni, AgX).
   - `Cycles_Fast_Preview.RGE`: Anteprima veloce e interattiva (128 campioni, rimbalzi ridotti, risoluzione al 50%).
   - `EEVEE_Next_High_Quality.RGE`: Configurazione ad alta fedeltà per EEVEE Next a 60 FPS con ombre morbide e Fast GI.
   - `Social_Media_Vertical_1080x1920.RGE`: Formato verticale 9:16 (1080x1920, 30 FPS) con sfondo trasparente.

---

## 📦 Installazione in Blender

### Metodo 1: Installazione da File Zip
1. Apri Blender (versione 3.6 LTS, 4.x o 5.x).
2. Vai su **Edit > Preferences > Add-ons**.
3. Clicca sulla freccia in alto a destra o sul menu e scegli **Install from Disk...** (oppure **Install...**).
4. Seleziona il file `RenderGate.zip` presente nella cartella `e:\RenderGate\`.
5. Spunta la casella per attivare l'add-on **RenderGate**.

### Metodo 2: Collegamento Diretto
Puoi copiare o creare un collegamento della cartella `RenderGate` all'interno della cartella `scripts/addons/` del tuo profilo Blender.

---

## 🖥️ Come si Usa

### 1. Dal Pannello "Render Properties"
1. Apri l'editor **Properties** e seleziona la scheda **Render** (icona della fotocamera).
2. In cima troverai il pannello **RenderGate Presets**:
   - **Menu a tendina**: seleziona uno dei preset predefiniti o personalizzati.
   - **Pulsante `+`**: salva le impostazioni di rendering attuali con un nuovo nome.
   - **Pulsante `-`**: elimina il preset personalizzato selezionato.
   - **Apply Selected Preset**: applica istantaneamente il preset alla scena attiva.
   - **Import .RGE... / Export .RGE...**: apre il File Browser di Blender per esportare o importare file ovunque sul tuo disco.

### 2. Dai Menu File Principali
- Per esportare: **File > Export > RenderGate Preset (.RGE)**
- Per importare: **File > Import > RenderGate Preset (.RGE)**

### 3. Report di Compatibilità
Se un preset contiene proprietà che appartengono a una versione di Blender differente:
- Comparirà un avviso nella barra di stato di Blender.
- Si aprirà la finestra di dialogo **RenderGate Compatibility Report**, che mostra:
  - Versione di origine vs Versione attuale di Blender.
  - Conteggio delle proprietà applicate e saltate.
  - Elenco dettagliato delle voci con valore e motivo.
  - Pulsante **Copy to Clipboard** per copiare il testo del log.
  - Pulsante **Send to Text Editor** per aprire il log completo nell'editor di testo interno di Blender (`RenderGate_Report.txt`).

---

## 📄 Struttura del File `.RGE`
Ecco un estratto di esempio di un file `.RGE`:

```json
{
  "_rendergate_meta": {
    "addon": "RenderGate",
    "addon_version": "1.0.0",
    "blender_version_str": "5.2.2 LTS",
    "preset_name": "Cycles_Production_4K_AgX",
    "description": "High quality Cycles 4K preset with AgX color management."
  },
  "categories": {
    "dimensions": {
      "category_label": "Dimensions & Framing",
      "properties": [
        {
          "field": "scene.render.resolution_x",
          "label": "Resolution X",
          "description": "Number of horizontal pixels in the rendered image",
          "type": "INT",
          "value": 3840
        },
        {
          "field": "scene.render.resolution_y",
          "label": "Resolution Y",
          "description": "Number of vertical pixels in the rendered image",
          "type": "INT",
          "value": 2160
        }
      ]
    },
    "color_management": {
      "category_label": "Color Management",
      "properties": [
        {
          "field": "scene.view_settings.view_transform",
          "label": "View Transform",
          "type": "ENUM",
          "value": "AgX"
        }
      ]
    }
  }
}
```
