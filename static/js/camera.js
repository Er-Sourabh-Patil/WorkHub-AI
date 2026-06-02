const video = document.getElementById('video');

navigator.mediaDevices.getUserMedia({
    video: {
        width: { ideal: 720 },
        height: { ideal: 720 },
        facingMode: "user"
    }
})
.then(stream => {
    video.srcObject = stream;
});


async function captureAndSend(){

    let attempts = 3;

    for(let i=0; i<attempts; i++){

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        const image = canvas.toDataURL('image/jpeg', 0.9);

        const res = await fetch('/api/mark_attendance', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({
                image:image,
                lat:0,
                lon:0
            })
        });

        const data = await res.json();

        if(data.status === "Success"){
            alert("Attendance Marked");
            return;
        }
    }

    alert("Face Not Recognized");
}