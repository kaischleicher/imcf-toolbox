from javax.swing import JScrollPane, JPanel, JComboBox, JLabel, JFrame
from java.awt import Color, GridLayout
from java.awt.event import ActionListener


class Listener(ActionListener):
  def __init__(self, label):
    self.label = label
  def actionPerformed(self, event):
    msg = "ActionListener called!"
    self.label.setText(msg)
    global frame
    frame.pack()


roimgr = RoiManager.getInstance()
rois = roimgr.getROIs()


choice_list = ["foo", "bar", "777"]

lbl1 = JLabel("foo label")
lbl2 = JLabel("bar label")

main_panel = JPanel()

### panel 1
panel1 = JPanel()
panel1.add(lbl1)
cb1 = JComboBox(choice_list)
panel1.add(cb1)

### panel 2
panel2 = JPanel()
panel2.add(lbl2)
cb2 = JComboBox(sorted(list(rois.keys())))
cb2.addActionListener(Listener(lbl2))
panel2.add(cb2)

frame = JFrame("Swing GUI Test Frame")
frame.getContentPane().add(main_panel)
main_panel.add(panel1)
main_panel.add(panel2)
frame.pack()
frame.setVisible(True)
