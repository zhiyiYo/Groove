#ifndef AERO_H
#define AERO_H

#include <QtWidgets/QDialog>
#include "ui_aero.h"
#include "mainframe.h"

class Aero : public QDialog
{
	Q_OBJECT

public:
	Aero(QWidget *parent = 0);
	~Aero();

	void paintEvent(QPaintEvent *);
	void mouseMoveEvent(QMouseEvent *event);
	void mousePressEvent(QMouseEvent *event);
	void mouseReleaseEvent(QMouseEvent *event);
	public slots:
	void showMin();
	void showColorD();
	void slotchBgColor(QColor);
	void slotsetAlph(int);
private:
	Ui::AeroClass ui;
	bool bFlag;
	QPoint m_startPos;
	QColor bgColor;
	mainframe *pmainframe;
	int m_alph;
};

#endif // AERO_H
