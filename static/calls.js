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

var commentTimeout;

$(".mark-posted").on("change", markPosted);
$(".mark-delivered").on("change", markDelivered);
$('.comment').on("change keyup paste", function(e) {
  clearTimeout(commentTimeout);
  commentTimeout = setTimeout(function() { submitComment(e) }, 500);
});
