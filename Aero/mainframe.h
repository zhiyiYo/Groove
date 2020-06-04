#ifndef MAINFRAME_H
#define MAINFRAME_H

#include <QDialog>
#include "ui_mainframe.h"

class mainframe : public QDialog
{
	Q_OBJECT

public:
	mainframe(QWidget *parent = 0);
	~mainframe();
	void paintEvent(QPaintEvent *event);
	void mouseMoveEvent(QMouseEvent *event);
	void mouseReleaseEvent(QMouseEvent *event);
	void mousePressEvent(QMouseEvent *event);
public slots:
	void showW();
	void slotvalueChanged(int);
signals:
	void chBgColor(QColor);
	void setAlph(int);
private:
	Ui::mainframe ui;
	QPoint m_startPos;
	QColor bgColor;
	QSlider *pslider;
	QVector<QLabel*> m_Vlabel;
	int m_alph;
};

#endif // MAINFRAME_H
