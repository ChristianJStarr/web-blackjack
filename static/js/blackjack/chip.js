import {createElement} from "./utility.js";
import {config} from "./config.js";

export class Chip {
    constructor(value) {
        this.url = `/static/chips/${config.chip_type}/${value}.svg`;
        this.node = createElement('div', 'chip');
        this.node.dataset.value = value;
        this.value = value;
        this.node.style.backgroundImage = `url("${this.url}")`;
    }
}