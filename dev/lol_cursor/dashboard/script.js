var socket = new WebSocket("ws://localhost:8000/ws")

socket.onopen = function (e) {
  console.log("[open] Connection established")
  console.log("Sending data to server")
  socket.send("SummonerName,Region") // replace with actual summoner name and region
}

socket.onmessage = function (event) {
  console.log(`[message] Data received from server: ${event.data}`)
  var data = JSON.parse(event.data)
  document.getElementById("summonerProfile").innerHTML = JSON.stringify(
    data.summonerProfile,
    null,
    2
  )
  document.getElementById("masteryStats").innerHTML = JSON.stringify(
    data.masteryStats,
    null,
    2
  )
  document.getElementById("leagueInfo").innerHTML = JSON.stringify(
    data.leagueInfo,
    null,
    2
  )
  document.getElementById("matchHistory").innerHTML = JSON.stringify(
    data.matchHistory,
    null,
    2
  )
  document.getElementById("performanceMetrics").innerHTML = JSON.stringify(
    data.performanceMetrics,
    null,
    2
  )
}

socket.onclose = function (event) {
  if (event.wasClean) {
    console.log(
      `[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`
    )
  } else {
    console.log("[close] Connection died")
  }
}

socket.onerror = function (error) {
  console.log(`[error] ${error.message}`)
}
