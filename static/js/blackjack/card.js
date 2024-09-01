import {createElement} from "./utility.js";
import {config} from "./config.js";

export class Card {
    constructor(card) {
        this.node = createElement('div', 'card');
        this.reset(card);
    }

    reset(card) {
        const {rank, suit} = this.parseCard(card);
        this.rank = rank;
        this.suit = suit;
        this.setImage();
    }

    setImage() {
        this.url = `/static/cards/${config.card_type}/${this.rank}${this.suit}.svg`;
        this.node.style.backgroundImage = `url("${this.url}")`;
    }

    parseCard(card) {
        let rank = 'B';
        let suit = '2';
        if(typeof card == "string"){
            rank = card.slice(1);
            suit = card.charAt(0);
        }
        else if(card && typeof card === "object"){
            rank = card.rank;
            suit = card.suit;
        }
        if(rank === 10) {
            rank = 'T';
        }

        return {rank, suit}
    }

}