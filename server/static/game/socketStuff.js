function socketSetup() {

    // General Socket Setup

    let dom = configs["domain"];

    socket = io.connect(dom);
    game_socket = io(dom + '/game');
    protect_socket = io(dom + '/protect');
    bet_socket = io(dom + '/bet');
    card_socket = io(dom + '/card');
    cont_socket = io(dom + '/cont');

}
