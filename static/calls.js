function markPosted(e) {
  var checked = this.checked;
  var sid = $(e.target).data("sid");
  $.post("/samordna/samtal-postad", {
    posted: checked,
    sid: sid,
    csrfmiddlewaretoken: window.CSRF_TOKEN,
  })
}

function markDelivered(e) {
  var checked = this.checked;
  var sid = $(e.target).data("sid");
  $.post("/samordna/samtal-levererad", {
    delivered: checked,
    sid: sid,
    csrfmiddlewaretoken: window.CSRF_TOKEN,
  })
}

function submitComment(e) {
  var $target = $(e.target);
  var text = $target.val();
  var sid = $target.data("sid");
  console.log(text, sid);
  $.post("/samordna/samtal-kommentar", {
    text: text,
    sid: sid,
    csrfmiddlewaretoken: window.CSRF_TOKEN,
  })
}

function updateCalls() {
  $.getJSON("/samordna/samtal-ajax", function(response) {
    for (var sid in response) {
      var $call = $(".call[data-sid=" + sid + "]");
      if ($call.length) {
        var c = response[sid];
        $(".mark-posted", $call)[0].checked = c.handled_at != null;
        $(".mark-delivered", $call)[0].checked = c.delivered_at != null;
        $(".comment", $call).val(c.comment);
      }
    }
  });
}

var commentTimeout;

$(".mark-posted").on("change", markPosted);
$(".mark-delivered").on("change", markDelivered);
$('.comment').on("change keyup paste", function(e) {
  clearTimeout(commentTimeout);
  commentTimeout = setTimeout(function() { submitComment(e) }, 500);
});

setInterval(updateCalls, 2000);
