var usernameInput = document.querySelector("#username");
var btnJoin = document.querySelector("#btn-join");

var mapPeers = {};
var username;
var webSocket;

function webSocketOnMessage(event) {
    var parsedData = JSON.parse(event.data);
    var peerUsername = parsedData['peer'];
    var action = parsedData['action'];

    if (username == peerUsername){
        return;
    }

    var receiver_channel_name = parsedData['message']['receiver_channel_name'];
    if(action == 'new-peer'){
        createOfferer(peerUsername, receiver_channel_name);
        return;
    }
    if(action == 'new-offer'){
        var offer = parsedData['message']['sdp'];
        createAnswerer(offer, peerUsername, receiver_channel_name);
        return;
    }
    if(action == 'new-answer'){
        var answer = parsedData['message']['sdp'];
        var peer = mapPeers[peerUsername][0];
        peer.setRemoteDescription(answer);
        return;
    }
}

btnJoin.addEventListener("click", ()=> { // Stablish a new WebSocket connection
    username = usernameInput.value;

    if (username.length < 1) {
        alert("Please enter a username.");
        return;
    }
    usernameInput.value = '';
    usernameInput.disabled = true;
    usernameInput.style.visibility = "hidden";

    btnJoin.disabled = true;
    btnJoin.style.visibility = "hidden";

    var labelUsername = document.querySelector("#label-username");
    labelUsername.innerHTML = "Welcome " + username + "!";

    var loc = window.location;
    var wsStart = 'ws://';

    if(loc.protocol == "https:") {
        wsStart = 'wss://';
    }

    var endpoint = wsStart + loc.host + loc.pathname;

    webSocket = new WebSocket(endpoint);

    webSocket.addEventListener("open", (event) => {
        console.log("Connection opened!", event);
        sendSignal('new-peer',{})
    });
    webSocket.addEventListener("message", webSocketOnMessage);
    webSocket.addEventListener("close", (event) => {
        console.log("Connection closed!", event);
    });
    webSocket.addEventListener("error", (event) => {
        console.log("Error", event);
    });
});

var localStream = new MediaStream();
const constraints = {
    'video': true,
    'audio': true
}

const localVideo = document.querySelector("#local-video");

const btnToggleAudio = document.querySelector("#btn-toggle-audio");
const btnToggleVideo = document.querySelector("#btn-toggle-video");

var userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localVideo.srcObject = localStream;
        localVideo.muted = true;

        var audioTracks = stream.getAudioTracks();
        var videoTracks = stream.getVideoTracks();

        audioTracks[0].enabled = true;
        videoTracks[0].enabled = true;

        btnToggleAudio.addEventListener("click", () => {
            audioTracks[0].enabled = !audioTracks[0].enabled;
            btnToggleAudio.innerHTML = audioTracks[0].enabled ? "Audio Mute" : "Audio Unmute";
        });

        btnToggleVideo.addEventListener("click", () => {
            videoTracks[0].enabled = !videoTracks[0].enabled;
            btnToggleVideo.innerHTML = videoTracks[0].enabled ? "Video Off" : "Video On";
        });
    })
    .catch(error => {
        console.error('Error accessing media devices.', error);
    });

function sendSignal(action, message){
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action,
        "message": message,
    });
    webSocket.send(jsonStr);     
}

function createOfferer(peerUsername, receiver_channel_name){
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);
    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('Connection opened!');
    });

    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;
        if (['failed', 'disconnected', 'closed'].includes(iceConnectionState)){
            delete mapPeers[peerUsername];
            if(iceConnectionState != 'closed'){
                peer.close();
            }
            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if(event.candidate){
            console.log('New ice candidate: ', JSON.stringify(peer.localDescription));
            return;
        }

        sendSignal('new-offer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });

    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))
        .then(() => {
            console.log('Local description set successfully!');
        });
}

function addLocalTracks(peer){
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    });
    return;
}

function createVideo(peerUsername){
    var videoContainer = document.querySelector("#video-container");

    var remoteVideo = document.createElement('video');
    remoteVideo.id = peerUsername + '-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;

    var videoWrapper = document.createElement('div');

    videoContainer.appendChild(videoWrapper);
    videoWrapper.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo){
    var remoteStream = new MediaStream()
    remoteVideo.srcObject = remoteStream;
    peer.addEventListener('track', async (event) => {
        remoteStream.addTrack(event.track, remoteStream);
    });
}

function removeVideo(video){
    var videoWrapper = video.parentNode;
    videoWrapper.parentNode.removeChild(videoWrapper); 
}

function createAnswerer(offer, peerUsername, receiver_channel_name){
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    peer.addEventListener('datachannel', (e) => {
        peer.dc = e.channel;
        peer.dc.addEventListener('open', () => {
            console.log('Connection opened!');
        });
        mapPeers[peerUsername] = [peer, peer.dc];
    });

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceConnectionState = peer.iceConnectionState;

        if (['failed', 'disconnected', 'closed'].includes(iceConnectionState)){
            delete mapPeers[peerUsername];
            
            if(iceConnectionState != 'closed'){
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if(event.candidate){
            console.log('New ice candidate: ', JSON.stringify(peer.localDescription));
            return;
        }
        sendSignal('new-answer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('Remote description set successfully for %s.!', peerUsername);
            return peer.createAnswer();
        })
        .then(answer => {
            console.log('Answer created!')
            peer.setLocalDescription(answer);
        });
}