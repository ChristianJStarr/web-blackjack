import {createElement} from "./utility.js";

export class Control {

    constructor(table) {
        this.table = table;

        this.node = createElement('div', 'control');
        this.audio_node = createElement('div', `control__audio ${this.table.game.audio_enabled?'-enabled':''}`);
        this.audio_node.textContent = 'Audio'

        this.node.append(
            this.audio_node,
        );

        this.audio_node.onclick = event => {
            this.table.game.audio_enabled = !this.table.game.audio_enabled;
            this.audio_node.className = `control__audio ${this.table.game.audio_enabled?'-enabled':''}`;
        }
    }
}