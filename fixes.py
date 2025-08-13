# todo, fixme, hack, note, bug, xxx
# NOTE: confirming an order process
#       1. customer adds goods to cart (creating cartItems)
#          when ready, customer orders (an order is created)
#       2. seller confirms the OrderItem (availibility checked),
#          or rejects it for any reason.
#       3. if all items are confired, admin confirms the Order \
#          and changes the status to processing,
#          otherwise, fails the Order and updates order explanation.
#       4. customer sees the status of order in its orders list,
#          if any order is rejected, chenges the quantity and tries again.
#          if the problem is not quantity and there's something wrong with \
#          the store, there is nothing that customer can do.

# FIXME: 1. OrderItem model: add a status field (confirmed, rejected, pending)
#        2. Order model: add an explanation field to order object \
#           (to say why rejected)
#        3. OrderItem view: for OrderItem we need views for single and mass \
#           cofirmation/reject, only be the seller. stock checking happens \
#           here, yet seller can rejects it manually for other reasons
#        4. Order view: single and mass confirmation for admin.
