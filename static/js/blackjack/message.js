import {createElement} from "./utility.js";

export class Message {

    constructor(table=null) {
        this.table = table;
        this.node = createElement('div', 'message');
        this.text_node = createElement('p', 'message__text');

        this.message = '';

        this.node.append(
            this.text_node,
        )
    }


    update(state) {
        let message;
        if(state?.result) {
            switch (state.result) {
                case 'win':
                    message = 'You Win';
                    break;
                case 'push':
                    message = 'You Push';
                    break;
                case 'lose':
                    message = 'You Lose';
                    break;
                default:
                    message = '';
            }
        }else {
            message = state?.message ?? '';
        }

        if (!(!message && this.temp_message) && message !== this.message) {
            this.setMessage(message);
        }

    }

    setTempMessage(message) {
        this.temp_message = message;
        this.setMessage(this.temp_message);
        setTimeout(() => {
            if (this.temp_message === message) {
                this.temp_message = '';
                this.setMessage(this.temp_message);
            }
        }, 2000);
    }

    setMessage(message) {
        this.text_node.textContent = message;
        this.message = message;
    }
}